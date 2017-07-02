import configuration.automation_settings as automation_settings

overtime_contribution = 0.021
rest_time_contribution = 0.016
email_reception_contribution = 0.0029
ambient_contribution = 0.0012
noise_contribution = 0.03
luminosity_contibution = 0.000153

if automation_settings.automate_tasks: tasks_automation_contribution = 0.25
else: tasks_automation_contribution = 0
