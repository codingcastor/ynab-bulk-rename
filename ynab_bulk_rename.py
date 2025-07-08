#!/usr/bin/env python3
"""
YNAB Bulk Rename Script

A CLI tool to bulk rename YNAB payees that match a specific pattern.
"""

__version__ = "0.1.0"

import argparse
import os
import re
import time
from typing import Dict, List

import requests


class YNABBulkRename:
    def __init__(self, bearer_token: str, budget_id: str, pattern: str):
        """
        Initialize the YNAB API client.

        Args:
            bearer_token: Your YNAB API bearer token
            budget_id: The budget ID to work with
            pattern: The regex pattern to match payees
        """
        self.bearer_token = bearer_token
        self.budget_id = budget_id
        self.base_url = "https://api.ynab.com/v1"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

        # Compile the custom regex pattern
        try:
            self.carte_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

    def _handle_rate_limit_response(self, response) -> bool:
        """
        Handle rate limit response and wait if necessary.

        Args:
            response: The HTTP response object

        Returns:
            True if we should retry, False otherwise
        """
        if response.status_code == 429:
            # Check if there's a Retry-After header
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait_time = int(retry_after)
                print(f"⚠️  Rate limit exceeded. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return True
            else:
                # Default wait time if no Retry-After header
                print("⚠️  Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return True
        return False

    def get_payees(self) -> List[Dict]:
        """
        Get all payees for the specified budget.

        Returns:
            List of payee dictionaries
        """
        url = f"{self.base_url}/budgets/{self.budget_id}/payees"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)

                # Handle rate limiting
                if response.status_code == 429:
                    if attempt < max_retries - 1:  # Don't retry on last attempt
                        if self._handle_rate_limit_response(response):
                            continue
                    else:
                        print("❌ Rate limit exceeded. Maximum retries reached.")
                        return []

                # Handle other HTTP errors
                if response.status_code == 401:
                    print("❌ Authentication failed. Please check your YNAB_TOKEN.")
                    return []
                elif response.status_code == 403:
                    print("❌ Access forbidden. Please check your token permissions.")
                    return []
                elif response.status_code == 404:
                    print(
                        f"❌ Budget not found. Please check your budget ID: {self.budget_id}"
                    )
                    return []

                response.raise_for_status()

                data = response.json()
                return data.get("data", {}).get("payees", [])

            except requests.ConnectionError:
                print(f"❌ Connection error. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                else:
                    print("❌ Connection failed after all retries.")
                    return []
            except requests.Timeout:
                print(f"❌ Request timeout. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                else:
                    print("❌ Request timed out after all retries.")
                    return []
            except requests.RequestException as e:
                print(f"❌ Error fetching payees: {e}")
                return []

        return []

    def update_payee(self, payee_id: str, new_name: str) -> bool:
        """
        Update a payee's name using the PATCH endpoint.

        Args:
            payee_id: The ID of the payee to update
            new_name: The new name for the payee

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/budgets/{self.budget_id}/payees/{payee_id}"
        payload = {"payee": {"name": new_name}}

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.patch(url, headers=self.headers, json=payload)

                # Handle rate limiting
                if response.status_code == 429:
                    if attempt < max_retries - 1:  # Don't retry on last attempt
                        if self._handle_rate_limit_response(response):
                            continue
                    else:
                        print(
                            f"❌ Rate limit exceeded for payee {payee_id}. Maximum retries reached."
                        )
                        return False

                # Handle other HTTP errors
                if response.status_code == 401:
                    print("❌ Authentication failed. Please check your YNAB_TOKEN.")
                    return False
                elif response.status_code == 403:
                    print("❌ Access forbidden. Please check your token permissions.")
                    return False
                elif response.status_code == 404:
                    print(f"❌ Payee not found: {payee_id}")
                    return False
                elif response.status_code == 400:
                    print(
                        f"❌ Bad request for payee {payee_id}. Check payee name: '{new_name}'"
                    )
                    return False

                response.raise_for_status()

                print(f"✅ Successfully renamed payee to: {new_name}")
                return True

            except requests.ConnectionError:
                print(
                    f"❌ Connection error updating payee {payee_id}. Attempt {attempt + 1}/{max_retries}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                else:
                    print(
                        f"❌ Connection failed for payee {payee_id} after all retries."
                    )
                    return False
            except requests.Timeout:
                print(
                    f"❌ Request timeout for payee {payee_id}. Attempt {attempt + 1}/{max_retries}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                else:
                    print(
                        f"❌ Request timed out for payee {payee_id} after all retries."
                    )
                    return False
            except requests.RequestException as e:
                print(f"❌ Error updating payee {payee_id}: {e}")
                return False

        return False

    def generate_new_name(self, original_name: str) -> str:
        """
        Generate a new name for the payee by removing the matched pattern.

        Args:
            original_name: The original payee name

        Returns:
            The new name with the pattern removed
        """
        match = self.carte_pattern.match(original_name)
        if match:
            # Remove the matched pattern from the beginning
            return self.carte_pattern.sub("", original_name).strip()

        return original_name

    def find_and_rename_payees(
        self, dry_run: bool = True, skip_pause: bool = False
    ) -> None:
        """
        Find payees matching the pattern and rename them.

        Args:
            dry_run: If True, only show what would be renamed without making changes
            skip_pause: If True, skip the pause between API calls
        """
        print("Fetching payees...")
        payees = self.get_payees()

        if not payees:
            print("No payees found or error occurred.")
            return

        matching_payees = []
        for payee in payees:
            name = payee.get("name", "")
            if self.carte_pattern.match(name):
                matching_payees.append(payee)

        if not matching_payees:
            print(f"No payees found matching the pattern: {self.carte_pattern.pattern}")
            return

        print(f"Found {len(matching_payees)} payees matching the pattern:")

        # Determine if we should pause between calls
        # Rate limit: 200 requests/hour = 1 fetch + up to 199 renames without pause
        should_pause = not skip_pause and len(matching_payees) >= 199

        if not dry_run:
            if skip_pause:
                print("⚡ Skipping pauses between API calls (--skip-pause enabled)")
                print(
                    "⚠️  Warning: This may cause rate limiting if you have many payees!"
                )
            elif len(matching_payees) < 199:
                print(
                    f"⚡ No pauses needed - {len(matching_payees)} payees is under rate limit (199)"
                )
            else:
                estimated_time = (
                    len(matching_payees) - 1
                ) * 20  # 20 seconds between requests
                print("⚠️  YNAB API Rate Limit: 200 requests/hour")
                print(
                    f"⏱️  Estimated completion time: ~{estimated_time // 60}m {estimated_time % 60}s"
                )
                print("    (20 second pause between each rename to stay within limits)")
            print()

        successful_renames = 0
        consecutive_failures = 0
        max_consecutive_failures = 5

        for i, payee in enumerate(matching_payees):
            payee_id = payee.get("id")
            original_name = payee.get("name", "")
            new_name = self.generate_new_name(original_name)

            print(f"  - {original_name} -> {new_name}")

            if not dry_run:
                success = self.update_payee(payee_id, new_name)

                if success:
                    successful_renames += 1
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        print(
                            f"❌ Stopping after {max_consecutive_failures} consecutive failures."
                        )
                        print(
                            f"   Successfully renamed {successful_renames} out of {i + 1} payees."
                        )
                        print("   This might be due to rate limiting or API issues.")
                        return

                # Add a pause between each API call if needed
                if (
                    should_pause and i < len(matching_payees) - 1
                ):  # Don't pause after the last one
                    print(
                        f"    ⏳ Pausing for 20 seconds... ({i + 1}/{len(matching_payees)} completed)"
                    )
                    time.sleep(20)

        if dry_run:
            print(
                "\n🔍 This was a dry run. To actually rename the payees, add --no-dry-run"
            )
        else:
            if successful_renames == len(matching_payees):
                print(f"\n✅ Successfully processed all {successful_renames} payees!")
            else:
                failed_count = len(matching_payees) - successful_renames
                print(
                    f"\n⚠️  Processed {successful_renames} out of {len(matching_payees)} payees."
                )
                print(f"   {failed_count} failed due to errors.")
                print("   Check the error messages above for details.")


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Bulk rename YNAB payees that match a specific pattern.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run with default pattern
  %(prog)s fedd1ee2-8048-4e69-95e5-cf2cab422dc5

  # Actually rename payees
  %(prog)s fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --no-dry-run

  # Custom pattern
  %(prog)s fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --pattern "^PAYMENT \\d{2}/\\d{2} "

  # Different pattern for merchant names
  %(prog)s fedd1ee2-8048-4e69-95e5-cf2cab422dc5 --pattern "^MERCHANT_PREFIX " --no-dry-run
        """,
    )

    parser.add_argument("budget_id", help="YNAB budget ID to work with")

    parser.add_argument(
        "--pattern",
        "-p",
        default=r"^CARTE \d{2}/\d{2} ",
        help="Regex pattern to match payees (default: '^CARTE \\d{2}/\\d{2} ')",
    )

    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually perform the rename operations (default: dry run only)",
    )

    parser.add_argument(
        "--skip-pause",
        action="store_true",
        help="Skip the pause between API calls to stay within rate limits (default: pause)",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def main():
    """
    Main function to run the bulk rename process.
    """
    args = parse_args()

    # Get bearer token from environment variable
    bearer_token = os.getenv("YNAB_TOKEN")

    if not bearer_token:
        print("❌ Error: YNAB_TOKEN environment variable not set!")
        print("Please set it with: export YNAB_TOKEN='your_token_here'")
        return 1

    try:
        # Initialize the renamer
        renamer = YNABBulkRename(bearer_token, args.budget_id, args.pattern)

        # Show configuration
        print(f"🎯 Budget ID: {args.budget_id}")
        print(f"🔍 Pattern: {args.pattern}")
        print(f"🏃 Mode: {'ACTUAL RENAME' if args.no_dry_run else 'DRY RUN'}")
        print("-" * 50)

        # Run the rename process
        renamer.find_and_rename_payees(
            dry_run=not args.no_dry_run, skip_pause=args.skip_pause
        )

        return 0

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
