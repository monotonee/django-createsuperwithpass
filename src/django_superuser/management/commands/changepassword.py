"""
Defines an override of contrib.auth's "changepassword" managment command.

A "password" option is added, allowing non-interactive setting of user passwords. In certain cases,
frameworks shouldn't be so opinionated and shouldn't try so hard to save the users from
themselves like contrib.auth's interactive-only password policy attempts to do. If I wanted to be
babysat like that, I'd be working with Microsoft products.

"""
