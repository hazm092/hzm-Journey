#!/usr/bin/env python3
"""
IAM User Activity Scanner
Lists all IAM users and reports when they last accessed AWS.
"""

import boto3
from datetime import datetime, timezone

def get_last_activity(user_name):
    """
    Determine the most recent activity for a given IAM user.
    Checks:
    1. Last console sign-in (PasswordLastUsed)
    2. Last use of any access key (API activity)
    Returns the most recent timestamp, or None if never active.
    """
    iam = boto3.client('iam')
    last_activity = None

    # STEP 1: Check if user has ever signed in to the console
    try:
        user = iam.get_user(UserName=user_name)['User']
        if 'PasswordLastUsed' in user:
            # This is the last time they logged into the AWS console
            last_activity = user['PasswordLastUsed']
    except Exception:
        # User might not have a console login (programmatic users)
        pass

    # STEP 2: Check all access keys for this user
    try:
        keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
        for key in keys:
            # Get the last time this specific key was used
            usage = iam.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
            if 'LastUsedDate' in usage['AccessKeyLastUsed']:
                key_last = usage['AccessKeyLastUsed']['LastUsedDate']
                # If this key was used more recently than the previous record, update
                if last_activity is None or key_last > last_activity:
                    last_activity = key_last
    except Exception:
        # User might not have any access keys
        pass

    return last_activity

def main():
    """
    Main function: Get all IAM users, analyse each, print results.
    """
    # Create an IAM client
    iam = boto3.client('iam')

    # Fetch all users from the AWS account
    try:
        users = iam.list_users()['Users']
    except Exception as e:
        print(f"Error fetching users: {e}")
        return

    print("IAM Users and Last Activity:\n")
    print(f"{'Username':<20} {'Last Activity'}")
    print("-" * 50)

    for user in users:
        name = user['UserName']
        last_activity = get_last_activity(name)

        if last_activity:
            # Convert to a readable format
            activity_time = last_activity.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{name:<20} {activity_time}")
        else:
            # Never used – inactive or newly created
            print(f"{name:<20} Never")

if __name__ == '__main__':
    main()
