# Python
import json, sys, traceback
import datetime

# Django
from django.shortcuts import render
from django.views.generic import (
	ListView,
	RedirectView,
	TemplateView
)
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

# Third Party
import pytz
import requests

# App
from .forms import SubmitJobForm
from .models import (
	InstagramContent,
	Job,
	Tag,
)


# ====================================================================================
# HELPERS
# ====================================================================================

def unix_to_date(unix_time):
    return datetime.datetime.fromtimestamp(
        int(unix_time)
    ).date()

# ====================================================================================
# VIEWS
# ====================================================================================

class DashboardView(TemplateView):

	template_name = "pixlee_app/base.html"

	def get_context_data(self, **kwargs):
		
		data = super(DashboardView, self).get_context_data(**kwargs)
		
		submit_job_form = SubmitJobForm()

		data.update({"submit_job_form": submit_job_form})

		return data

class LandingView(RedirectView):

	def get_redirect_url(self, *args, **kwargs):
		return (
			"https://instagram.com/oauth/authorize/"
			"?client_id=d64c4125fbb642e8ae41d9d8e696664a"
			"&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fdashboard%2F&response_type=token"
		)

@csrf_exempt
def get_status_view(request):

	running_jobs = list(Job.objects.filter(
		job_end_datetime__isnull=True
	).values(
		"pk",
		"tag__name",
		"from_date",
		"to_date",
		"job_start_datetime",
		"job_end_datetime",
		"image_count",
		"checked_pages",
		"last_modified_datetime",
	).order_by(
		"-job_start_datetime"
	))

	# Only allow unresponsive jobs to be reset.
	# Assuming 10 seconds of no updates to be "unresponsive"
	right_now = datetime.datetime.now(pytz.utc)
	ten_seconds_ago = right_now - datetime.timedelta(seconds=10)
	for job in running_jobs:
		if job.get("last_modified_datetime") < ten_seconds_ago:
			job.update({"ok_to_reboot": 1})

	data = {
		"success": True,
		"jobs": running_jobs
	}

	return JsonResponse(
		data=data
	)

@csrf_exempt
def submit_job_view(request):

	submit_form = SubmitJobForm(
		data=request.POST
	)
	if submit_form.is_valid():

		try:
			tag, created = Tag.objects.update_or_create(
				name=request.POST.get("tag").lower()
			)

			job = Job.objects.create(
				tag=tag,
				from_date=submit_form.cleaned_data.get("from_date"),
				to_date=submit_form.cleaned_data.get("to_date"),
			)

			scan_tagged_content(
				job=job,
				access_token=request.POST.get("access_token"),
			)
		except:
			traceback.print_exc(file=sys.stdout)
	else:
		print submit_form.errors

	return JsonResponse(
		data={
			"success": True,
		}
	)

@csrf_exempt
def reboot_job_view(request):

	job = Job.objects.get(
		pk=request.POST.get("pk")
	)

	# Save job to update it's last_modified field
	job.save()

	access_token = request.POST.get("access_token")

	scan_tagged_content(job, access_token)

	return JsonResponse(
		data={
			"success": True,
		}
	)

def scan_tagged_content(job, access_token):

	base_url = "https://api.instagram.com/v1/tags/{tag}/media/recent".format(tag=job.tag.name)
	payload = {
		"access_token": access_token,
		"q": job.tag,
		"count": 35,  # The API seems to max out at 35 objects per page for the time being
	}

	# If job has last_max_tag_id, it means we're requesting to reboot a previously stopped job.
	# Update the payload to restart from where we left off
	if job.last_max_tag_id:
		payload.update({
		"max_tag_id": job.last_max_tag_id
	})

	continue_job = True
	while continue_job:

		r = requests.get(
			base_url,
			params=payload
		)

		# Break if we don't have a 200 success status
		if r.status_code != 200:
			continue_job = False
			break

		# Ensure we're still over our rate limit
		headers = r.headers
		try:
			rate_limit_remaining = int(headers.get("X-Ratelimit-Remaining"))
			if rate_limit_remaining <= 0:
				continue_job = False
		except TypeError:
			continue_job = False
			break

		# Iterate through each content object in page data
		page = json.loads(r.text)
		saved_image_count = job.image_count

		for content in page.get("data"):
			username = content.get("user").get("username")
			tag_date = get_tag_date(job.tag, username, content)

			# Skip if not photo
			if content.get("type") != "image":
				continue

			# Skip if no tag date found
			if not tag_date:
				continue
	
			# If tag_time is on or before job.from_date, we've gone too far in the past.
			# Stop the job
			if tag_date <= job.from_date:
				continue_job = False
				break
			
			# If tag_time is between from and to dates, populate content
			if job.from_date < tag_date < job.to_date:
				
				instagram_image = InstagramContent.objects.create(
					tag=job.tag,
					tag_date=tag_date,
					instagram_id=content.get("id"),
					image_url=content.get("images").get("thumbnail").get("url")
				)

				instagram_image.get_remote_image()

				saved_image_count += 1

		# If we're still within our job range, update max_id param and make new request
		next_max_tag_id = page.get("pagination").get("next_max_tag_id")
		payload.update({
			"max_tag_id": next_max_tag_id
		})

		# Update job
		job.last_max_tag_id = next_max_tag_id
		job.image_count = saved_image_count
		job.checked_pages += 1
		job.save()

	# End the job
	job.job_end_datetime = datetime.datetime.now()
	job.save()
		

def get_tag_date(tag, username, content):

	hashed_tag = "#" + tag.name
	tag_time = None

	# Find tag_time in caption
	caption = content.get("caption")
	if caption:
		tag_time = caption.get("created_time")

	# See if original poster put tag in comment
	comments = content.get("comments").get("data")
	if comments:
		try:
			original_poster_tag_comment = filter(
				lambda x: all([
					x.get("from").get("username") == username,
					hashed_tag in x.get("text")
				]),
				comments
			)[0]

			tag_time = original_poster_tag_comment.get("created_time")

		except IndexError:
			# Original poster did not have a comment with the tag in it.
			# Continue to use the caption created time
			pass

	# Convert time from unix time
	if tag_time:
		tag_date = unix_to_date(tag_time)
		return tag_date
	else:
		return None

