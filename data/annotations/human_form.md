# HUMAN VALIDATION FORM (fill this file)
For each CONDITION write y (covered), p (partial), n (not tested) for Baseline(B) and Refined(R).
For each EDGE SCENARIO write y/n for B and R.
Oracle check: if any expected_result clearly contradicts the requirement, note it under 'Oracle issues'.

================================================================================
## REQ-02
REQUIREMENT: The system shall allow users to reset their password via a link sent to their registered email. The reset link shall expire after 15 minutes.

### Conditions
- User requests a password reset.
    B:    R: 
- System sends a password reset email.
    B:    R: 
- User clicks the reset link.
    B:    R: 
- User enters a new password.
    B:    R: 
- System updates the user's password.
    B:    R: 

### Edge scenarios
- User clicks the reset link after 15 minutes.
    B:    R: 
- User clicks the reset link after 16 minutes.
    B:    R: 
- User clicks the reset link immediately.
    B:    R: 
- User uses another user's reset link.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Successful password reset via email link
  - Password reset link expires after 15 minutes
  - Password reset link works exactly at 15 minutes
  - No reset link sent for non-existent email

### Refined test case titles:
  - Successful password reset via email link
  - Password reset link expires after 15 minutes
  - Password reset link works exactly at 15 minutes
  - No reset link sent for non-existent email
  - Invalid reset token format
  - Reset link is single-use
  - Password does not meet complexity requirements

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-04
REQUIREMENT: The system shall allow a user to add a product to the shopping cart. The same product added twice shall increase the quantity instead of creating a duplicate entry.

### Conditions
- User can add a product to the shopping cart.
    B:    R: 
- System creates a new cart entry for a new product.
    B:    R: 
- System increments the quantity for an existing product.
    B:    R: 
- System prevents duplicate product entries.
    B:    R: 

### Edge scenarios
- Adding the same product twice in rapid succession.
    B:    R: 
- Adding a product with a quantity of 0.
    B:    R: 
- Adding a product that is already in the cart with the maximum allowed quantity.
    B:    R: 
- Attempting to add a product with a negative quantity.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Add first item to empty cart
  - Add same product again to increment quantity
  - Add same product multiple times
  - Add different product to cart

### Refined test case titles:
  - Add first item to empty cart
  - Increment quantity of existing item
  - Increment quantity multiple times
  - Add different product to cart
  - Add same product to cart containing other items

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-05
REQUIREMENT: During checkout, the user shall enter a valid 16-digit card number. Invalid or expired cards shall be rejected with an appropriate error message.

### Conditions
- System accepts a 16-digit numeric card number.
    B:    R: 
- System rejects a card number with fewer than 16 digits.
    B:    R: 
- System rejects a card number with more than 16 digits.
    B:    R: 
- System rejects a card number containing non-numeric characters.
    B:    R: 
- System rejects an invalid card number (fails Luhn check).
    B:    R: 
- System rejects an expired card.
    B:    R: 

### Edge scenarios
- Inputting a card number with spaces or dashes.
    B:    R: 
- Inputting a 15-digit card number.
    B:    R: 
- Inputting a 17-digit card number.
    B:    R: 
- Submitting an empty card number field.
    B:    R: 
- Entering a card with a past expiry date.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Enter valid 16-digit card number
  - Enter card number with incorrect length
  - Enter expired card

### Refined test case titles:
  - Enter valid 16-digit card number
  - Enter card number with incorrect length
  - Enter expired card
  - Enter card number containing letters
  - Enter card number with 17 digits
  - Enter empty card number

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-08
REQUIREMENT: The search field shall accept a minimum of 2 characters. If the user enters special characters, the system shall sanitize the input before searching.

### Conditions
- System accepts search input with exactly 2 characters.
    B:    R: 
- System rejects search input with fewer than 2 characters.
    B:    R: 
- System sanitizes special characters in the input string.
    B:    R: 
- System processes the sanitized input for search results.
    B:    R: 

### Edge scenarios
- Inputting exactly 1 character triggers a validation error.
    B:    R: 
- Inputting only special characters (e.g., '@#$') executes a search.
    B:    R: 
- Inputting mixed alphanumeric and special characters (e.g., 'ab@cd') executes a sanitized search.
    B:    R: 
- Inputting zero characters triggers a validation error.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Search with valid input (minimum 2 characters)
  - Search with input less than 2 characters
  - Search with special characters
  - Search with alphanumeric and special characters

### Refined test case titles:
  - Search with valid input (minimum 2 characters)
  - Search with input less than 2 characters
  - Search with special characters
  - Search with alphanumeric and special characters
  - Search with empty input
  - Search with input less than 2 characters containing special characters
  - Search with input exactly 2 characters containing special characters

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-16
REQUIREMENT: The user shall be able to cancel an order within 30 minutes of placement. After cancellation, a refund shall be initiated to the original payment method.

### Conditions
- User can cancel order if placed less than 30 minutes ago.
    B:    R: 
- User cannot cancel order if placed more than 30 minutes ago.
    B:    R: 
- User cannot cancel order exactly 30 minutes after placement.
    B:    R: 
- Refund is initiated immediately upon successful cancellation.
    B:    R: 
- Refund is processed to the original payment method.
    B:    R: 
- Refund amount matches the original order total.
    B:    R: 

### Edge scenarios
- Attempting to cancel exactly at the 30-minute mark.
    B:    R: 
- Attempting to cancel an order placed 31 minutes ago.
    B:    R: 
- Refund fails due to payment gateway error.
    B:    R: 
- Canceling an order with a pending partial payment.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Cancel order within 30 minutes
  - Cancel order after 30 minutes
  - Verify refund to original payment method

### Refined test case titles:
  - Cancel order within 30 minutes
  - Cancel order after 30 minutes
  - Verify refund to original payment method
  - Cancel order exactly at 30 minutes
  - Cancel order paid via Debit Card

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-18
REQUIREMENT: New accounts shall be activated through a verification link sent by email. The link shall expire after 24 hours, after which a new link can be requested.

### Conditions
- Email is sent immediately after registration.
    B:    R: 
- Clicking the verification link activates the account.
    B:    R: 
- The verification link remains valid for exactly 24 hours.
    B:    R: 
- Clicking the link after 24 hours results in failure.
    B:    R: 
- A new verification link can be requested after the previous one expires.
    B:    R: 
- Clicking the link multiple times does not create duplicate accounts.
    B:    R: 

### Edge scenarios
- Clicking the link exactly at the 24-hour expiration boundary.
    B:    R: 
- Clicking the link 1 minute after the expiration time.
    B:    R: 
- Requesting a new verification link while the previous one is still valid.
    B:    R: 
- Clicking a verification link from a different user's email.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Activate account using valid verification link
  - Account activation with expired link
  - Request new verification link after expiration

### Refined test case titles:
  - Activate account using valid verification link
  - Account activation with expired link
  - Request new verification link after expiration
  - Account activation with link exactly at 24-hour expiry
  - Activate account using valid link multiple times (Idempotency)

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-22
REQUIREMENT: Search results shall be paginated with 20 items per page. If the user navigates beyond the last page, an empty state message shall be shown.

### Conditions
- First page displays exactly 20 results.
    B:    R: 
- Second page displays the next 20 results.
    B:    R: 
- Total page count is calculated correctly.
    B:    R: 
- Previous button is disabled on page 1.
    B:    R: 
- Next button is disabled on the last page.
    B:    R: 
- Pagination controls are visible.
    B:    R: 

### Edge scenarios
- Clicking 'Next' on the last page shows the empty state message.
    B:    R: 
- Clicking 'Next' on the last page does not crash the application.
    B:    R: 
- Clicking 'Next' on the last page keeps the user on the last page.
    B:    R: 
- Search returns 0 results and displays empty state.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Verify first page displays 20 items
  - Verify second page displays 20 items
  - Navigate beyond last page using Next button
  - Navigate to non-existent page number

### Refined test case titles:
  - Verify first page displays 20 items
  - Verify second page displays 20 items
  - Navigate beyond last page using Next button
  - Navigate to non-existent page number
  - Verify Previous button is disabled on Page 1

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-24
REQUIREMENT: The application shall support English and Chinese. The selected language shall persist across sessions and apply to all menus and messages.

### Conditions
- Application provides English language selection option.
    B:    R: 
- Application provides Chinese language selection option.
    B:    R: 
- Switching to English updates all interface text.
    B:    R: 
- Switching to Chinese updates all interface text.
    B:    R: 
- Language preference persists after application restart.
    B:    R: 
- All menus display in the selected language.
    B:    R: 
- All messages display in the selected language.
    B:    R: 

### Edge scenarios
- Language preference reverts to default after application crash.
    B:    R: 
- Some interface elements fail to translate after language switch.
    B:    R: 
- Switching languages while a transaction is in progress.
    B:    R: 
- Switching between languages multiple times rapidly.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Switch application language to English
  - Switch application language to Chinese
  - Verify English language persists after session refresh
  - Verify Chinese language persists after session refresh
  - Verify language applies to navigation menus
  - Verify language applies to system messages

### Refined test case titles:
  - Switch application language to English
  - Switch application language to Chinese
  - Verify English language persists after session refresh
  - Verify Chinese language persists after session refresh
  - Verify language applies to navigation menus
  - Verify language applies to system messages
  - Verify English language persists after closing and reopening the browser
  - Verify language applies to buttons and input placeholders
  - Verify language switches correctly while a modal is open

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-29
REQUIREMENT: The system shall generate a monthly usage report as a PDF on the first day of each month. If generation fails, an email alert shall be sent to the administrator.

### Conditions
- System generates the monthly usage report on the first day of the month.
    B:    R: 
- The generated report is in PDF format.
    B:    R: 
- The report contains usage data.
    B:    R: 
- System sends an email alert to the administrator if generation fails.
    B:    R: 
- System does not send an email alert if generation succeeds.
    B:    R: 

### Edge scenarios
- Report generation fails on the first day of the month.
    B:    R: 
- Generated PDF file is empty or corrupted.
    B:    R: 
- Email alert fails to send due to server error.
    B:    R: 
- Report is generated after the first day of the month.
    B:    R: 
- Administrator email address is invalid.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Generate monthly usage report as PDF on the first day of the month
  - Send email alert to administrator if report generation fails

### Refined test case titles:
  - Generate monthly usage report as PDF on the first day of the month
  - Send email alert to administrator if report generation fails
  - Verify no automatic report generation on days other than the first of the month

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)

================================================================================
## REQ-35
REQUIREMENT: The mobile application shall support biometric login using fingerprint or face recognition. After 5 failed biometric attempts, PIN entry shall be required.

### Conditions
- System accepts valid fingerprint for login.
    B:    R: 
- System accepts valid face recognition for login.
    B:    R: 
- System rejects invalid fingerprint attempts.
    B:    R: 
- System rejects invalid face recognition attempts.
    B:    R: 
- System prompts for PIN after 5 failed biometric attempts.
    B:    R: 
- System accepts valid PIN after 5 failed attempts.
    B:    R: 

### Edge scenarios
- System requires PIN entry after exactly 5 failed attempts.
    B:    R: 
- System resets the failed attempt counter after a successful login.
    B:    R: 
- System handles biometric hardware unavailability gracefully.
    B:    R: 
- System allows PIN entry when biometric permissions are denied.
    B:    R: 

Oracle issues (write 'none' or describe):

### Baseline test case titles:
  - Successful Biometric Login
  - Failed Biometric Login (First Attempt)
  - PIN Required after 5 Failed Biometric Attempts
  - Successful PIN Entry after Biometric Lockout
  - Failed PIN Entry after Biometric Lockout
  - Biometric attempts reset after logout

### Refined test case titles:
  - Successful Biometric Login
  - Failed Biometric Login (First Attempt)
  - PIN Required after 5 Failed Biometric Attempts
  - Successful PIN Entry after Biometric Lockout
  - Failed PIN Entry after Biometric Lockout
  - Biometric attempts reset after logout
  - Biometric Login when Sensor is Disabled or Unavailable
  - Biometric Login Cancelled by User
  - Logout during Biometric Attempt Sequence

(Full test case details: outputs/baseline/ and outputs/feedback/ files - open if titles are not enough)