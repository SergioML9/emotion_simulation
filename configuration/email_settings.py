import configuration.automation_settings as automation_settings

if automation_settings.automate_emails:
    emails_read_distribution_params = 4.70, 4.1
else:
    emails_read_distribution_params = 12.54, 8.02  #12.54, 8.02 (unlimited) or 4.70 4.1 (limited)
email_read_time_distribution_params = 3, 0.5 # TODO: search for real values
