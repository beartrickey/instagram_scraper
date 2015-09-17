from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, HTML

class SubmitJobForm(forms.Form):
	
	tag = forms.CharField(max_length=50, required=True)
	from_date = forms.DateField()
	to_date = forms.DateField()

	def __init__(self, *args, **kwargs):
		super(SubmitJobForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.layout = Layout(
			Fieldset(
				"Job Form",
				"tag",
				"from_date",
				"to_date",
				HTML(
					'''
					<div class="form-group">
						<button type="button" class="btn btn-primary" onclick="submitJob()">
							<i class="fa fa-plus"></i> Submit
						</button>
					</div>
					'''
				),
			)
		)

