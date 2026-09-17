# Failure Analysis

An analysis of the current system reveals five primary failure modes across the intent classification and escalation pipeline.

## 1. Multiple symptoms / competing intents
When a customer mentions multiple issues, the classifier may trigger on secondary symptoms due to keyword priority.
- **Example**: "Anyone else having issues since this #ios1103 update? my batter dies fast. Speaker doesn’t work on phone + glitched"
- **Gold**: `battery_charging`
- **Predicted**: `hardware_display`
- **Cause**: Multiple valid keywords trigger different intents.
- **Hypothesis**: Detect the primary customer symptom rather than relying only on keyword priority.

## 2. Generic update language overwhelms the actual problem
Customers frequently mention recent software updates as context for their actual hardware or app issue.
- **Example**: "the 11.0.3 upgrade caused some irritating earpod audio jack issues for iphone 6s."
- **Gold**: `hardware_display`
- **Predicted**: `ios_update`
- **Cause**: The classifier gives strong priority to update-related terms.
- **Hypothesis**: Treat software-update references as contextual unless the update itself is the actual support problem.

## 3. Ambiguous how-to / feature requests
Questions about how to use a feature can easily be confused with bug reports when they share terminology.
- **Example**: "How do you close a app when it crashes? When you had the home button you could double tap and force quit!"
- **Gold**: `other_insufficient_information`
- **Predicted**: `app_issue`
- **Cause**: The classifier recognizes "app" and "crashes" but misses the how-to nature of the request.
- **Hypothesis**: Separate how-to/feature requests from concrete technical failures.

## 4. Account/data cases overlap lexically
Account access issues and data management issues often share terminology (e.g., "icloud").
- **Example**: "absolutely rubbish service trying to get into icloud following factory reset"
- **Gold**: `apple_id_account`
- **Predicted**: `icloud_data`
- **Cause**: The word "icloud" occurs in both account and data-related cases.
- **Hypothesis**: Use the relationship between the action and entity, e.g. login/access versus backup/sync/data.

## 5. Escalation depends too heavily on retrieval availability
The escalation policy sometimes fails to escalate inherently risky queries simply because historical retrieval evidence is found.
- **Example**: "Is a full backup required before downloading the latest iOS?"
- **Gold escalation**: `ESCALATE`
- **Predicted**: `AUTO-HANDLE`
- **Cause**: The policy sees a supported intent and historical evidence and therefore chooses AUTO-HANDLE.
- **Hypothesis**: Escalation should incorporate risk, uncertainty, persistence, account/data concerns and case-specific investigation instead of relying primarily on retrieval availability.
