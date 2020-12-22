from functions import db_submit, text_send

db_submit('monthly_budget_add')
message = 'money has been added to the budgets and  reconciliation can be done for last month. Go here for reconciliation report - www.brandonruggles.com/reconcile'
nums = ['+14357703097','4692681192']
for number in nums:
    text_send(body=message, to = number)


