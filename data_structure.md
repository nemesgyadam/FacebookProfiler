# Facebook Profile Data Structure Analysis

## Project Overview
Based on the README, this project aims to create a detailed psychological profile from Facebook data for mental health analysis and trauma resolution.

**Note**: The `start.md` file mentioned was not found in the repository.

## Data Folder Overview
The `data` folder contains **987 items** organized into 8 main categories representing different aspects of Facebook data export.

## Main Categories

### 1. `ads_information/` (9 items)
Contains advertising-related data and preferences:
- `ad_preferences.json` (19.8KB) - User's advertising preferences
- `advertisers_using_your_activity_or_information.json` (47.1KB) - Advertisers with access to user data
- `advertisers_you've_interacted_with.json` (2.5KB) - Interaction history with ads
- `meta_ad_library_accounts.json` (412B) - Meta ad library account information
- `other_categories_used_to_reach_you.json` (2.2KB) - Additional targeting categories
- `story_views_in_past_7_days.json` (153B) - Recent story interaction data
- `subscription_for_no_ads.json` (161B) - Ad-free subscription information
- `your_consent_settings.json` (258B) - Privacy consent preferences
- `your_meta_business_suite_guidance_interactions.json` (239B) - Business suite interactions

### 2. `apps_and_websites_off_of_facebook/` (5 items)
Data about external app and website interactions connected to Facebook account.

### 3. `connections/` (9 items)
Social connections and relationship data including friends, followers, and blocked users.

### 4. `logged_information/` (23 items)
System logs and technical information about account usage and activities.

### 5. `personal_information/` (18 items)
Personal profile data organized in subdirectories:
- `avatars/` (1 item) - Profile avatar data
- `avatars_store/` (1 item) - Avatar store information
- `facebook_accounts_center/` (1 item) - Account center data
- `other_personal_information/` (6 items) - Additional personal details
- `profile_information/` (9 items) - Core profile information

### 6. `preferences/` (23 items)
User preferences and settings across different Facebook features.

### 7. `security_and_login_information/` (14 items)
Security-related data including login history, device information, and authentication settings.

### 8. `your_facebook_activity/` (886 items) - **LARGEST CATEGORY**
The most substantial section containing detailed activity data:

#### Major Subcategories:
- **`messages/` (551 items)** - The largest subcategory containing:
  - `ai_conversations.json` (11.8KB) - AI chat history
  - `archived_threads/` (3 items) - Archived conversations
  - `e2ee_cutover/` (215 items) - End-to-end encryption data
  - `filtered_threads/` (13 items) - Filtered messages
  - `inbox/` (299 items) - Main message conversations
  - `photos/` - Message-related media
  - `stickers_used/` (5 items) - Sticker usage data
  - Various messaging settings and configurations (multiple JSON files)

- **`posts/` (275 items)** - User's posts and timeline content

- **`groups/` (13 items)** - Facebook groups activity and membership

- **`other_activity/` (12 items)** - Miscellaneous Facebook activities

- **`events/` (5 items)** - Event-related data

- **`facebook_marketplace/` (5 items)** - Marketplace activity

- **`comments_and_reactions/` (4 items)** - User's comments and reactions

- **`dating/` (3 items)** - Facebook Dating data

- **`facebook_gaming/` (3 items)** - Gaming platform activity

- **`navigation_bar/` (3 items)** - Navigation usage patterns

- **`fundraisers/` (3 items)** - Fundraising activities

- **`facebook_payments/` (2 items)** - Payment transaction data

- **`pages/` (2 items)** - Pages interaction data

- **`voting/` (2 items)** - Voting and poll activities

- **`polls/` (1 item)** - Poll participation

- **`stories/` (1 item)** - Stories activity

- **`your_places/` (1 item)** - Location and places data

## Data Characteristics

### File Formats
- **JSON files**: Primary format for structured data
- **Subdirectories**: Organizational structure for related content
- **Media folders**: Contain photos and multimedia content

### Key Insights for Psychological Analysis
1. **Communication Patterns**: Extensive messaging data (551 items) provides rich behavioral insights
2. **Social Interactions**: Comments, reactions, and posts reveal social engagement patterns
3. **Interest Mapping**: Ad preferences and interactions show personal interests and values
4. **Behavioral Timeline**: Activity across posts, events, and interactions creates temporal behavior patterns
5. **Privacy Awareness**: Security settings and consent data indicate privacy consciousness

### Data Volume Distribution
- **Messages**: ~56% of activity data (551/886 items)
- **Posts**: ~31% of activity data (275/886 items)
- **Other Activities**: ~13% combined (remaining categories)

## Recommendations for Analysis
1. **Start with messaging data** - highest volume and behavioral richness
2. **Analyze post content and timing** - reveals interests and communication style
3. **Cross-reference ad preferences** - validates interest mapping
4. **Timeline analysis** - track behavioral evolution over time
5. **Social network mapping** - understand relationship patterns from connections and interactions

## Technical Notes
- Total data points: 987 items across all categories
- Largest single file: `advertisers_using_your_activity_or_information.json` (47.1KB)
- Most complex category: `your_facebook_activity/messages/` with nested subdirectories
- Data appears to be complete Facebook export including encrypted messaging data
