#!/usr/bin/env python3
"""
Script: list_iam_users.py
Purpose: List all IAM users and their last activity time.
"""
import boto3
from datetime import datetime, timezone
import sys

def get_last_activity(user_name):
    """
    Determine the most recent activity for a user by checking:
    - Last console sign‑in
    - Last use of any access key
    """
    iam = boto3.client('iam')
    last_activity = None

    # 1. Console sign‑in (if exists)
    try:
        login_profile = iam.get_login_profile(UserName=user_name)
        # If they have a console login, we can get the last sign‑in time
        # via iam.get_user, but we'll do it separately
    except iam.exceptions.NoSuchEntityException:
        pass  # no console login

    # 2. Get user details (includes password last used)
    user = iam.get_user(UserName=user_name)['User']
    if 'PasswordLastUsed' in user:
        last_activity = user['PasswordLastUsed']

    # 3. Check access keys for last used date
    keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
    for key in keys:
        # Get key usage details
        try:
            usage = iam.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
            if 'LastUsedDate' in usage['AccessKeyLastUsed']:
                key_last = usage['AccessKeyLastUsed']['LastUsedDate']
                if last_activity is None or key_last > last_activity:
                    last_activity = key_last
        except Exception:
            continue

    return last_activity

def main():
    iam = boto3.client('iam')
    try:
        users = iam.list_users()['Users']
    except Exception as e:
        print(f"Error listing users: {e}")
        sys.exit(1)

    print("IAM Users and Last Activity:\n")
    for user in users:
        name = user['UserName']
        last_activity = get_last_activity(name)
        if last_activity:
            # Convert to local time if needed (optional)
            print(f"{name:20} Last used: {last_activity}")
        else:
            print(f"{name:20} Last used: Never")

if __name__ == '__main__':
    main()
