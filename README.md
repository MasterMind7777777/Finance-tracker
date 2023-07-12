
# Financial Management System API

The Financial Management System API provides a set of endpoints to manage and track financial activities. It offers functionalities for analytics, budgets, transactions, and user management. This document outlines the available endpoints and their functionalities.

## Table of Contents

-   [Analytics](https://chat.openai.com/#analytics)
    -   [Analytics View](https://chat.openai.com/#analytics-view)
    -   [Fetch Sticky Notes](https://chat.openai.com/#fetch-sticky-notes)
    -   [Create or Add to Board](https://chat.openai.com/#create-or-add-to-board)
    -   [Fetch Board Sticky Notes](https://chat.openai.com/#fetch-board-sticky-notes)
    -   [Delete Sticky Note from Board](https://chat.openai.com/#delete-sticky-note-from-board)
    -   [Save Board](https://chat.openai.com/#save-board)
    -   [Fetch User Boards](https://chat.openai.com/#fetch-user-boards)
    -   [Savings Opportunities](https://chat.openai.com/#savings-opportunities)
    -   [Create Financial Health](https://chat.openai.com/#create-financial-health)
-   [Budgets](https://chat.openai.com/#budgets)
    -   [Budget Overview](https://chat.openai.com/#budget-overview)
    -   [Delete Budget](https://chat.openai.com/#delete-budget)
    -   [Category Budget ViewSet](https://chat.openai.com/#category-budget-viewset)
-   [Transactions](https://chat.openai.com/#transactions)
    -   [Add Transaction](https://chat.openai.com/#add-transaction)
    -   [Delete Transaction](https://chat.openai.com/#delete-transaction)
    -   [Categories View](https://chat.openai.com/#categories-view)
    -   [Manage Categories](https://chat.openai.com/#manage-categories)
    -   [Delete Category](https://chat.openai.com/#delete-category)
    -   [Transaction List](https://chat.openai.com/#transaction-list)
    -   [Transaction Detail](https://chat.openai.com/#transaction-detail)
    -   [Forecast Expenses](https://chat.openai.com/#forecast-expenses)
    -   [Category ViewSet](https://chat.openai.com/#category-viewset)
    -   [Transaction ViewSet](https://chat.openai.com/#transaction-viewset)
-   [Users](https://chat.openai.com/#users)
    -   [Signup](https://chat.openai.com/#signup)
    -   [User Login](https://chat.openai.com/#user-login)
    -   [User Logout](https://chat.openai.com/#user-logout)
    -   [Dashboard](https://chat.openai.com/#dashboard)
    -   [User ViewSet](https://chat.openai.com/#user-viewset)
-   [Capital](https://chat.openai.com/#capital)
    -   [Saving Goal ViewSet](https://chat.openai.com/#saving-goal-viewset)
-   [Database Models](https://chat.openai.com/#database-models)

## Analytics

### Analytics View

-   Endpoint: `/analytics_view`
-   Method: GET
-   Description: Displays the user's financial analytics.

### Fetch Sticky Notes

-   Endpoint: `/fetch_sticky_notes`
-   Method: GET
-   Description: Retrieves all sticky notes as JSON.

### Create or Add to Board

-   Endpoint: `/create_or_add_to_board`
-   Method: POST
-   Description: Creates or modifies a board.

### Fetch Board Sticky Notes

-   Endpoint: `/fetch_board_sticky_notes`
-   Method: GET
-   Description: Fetches sticky notes for a specific board.

### Delete Sticky Note from Board

-   Endpoint: `/delete_sticky_note_from_board`
-   Method: POST
-   Description: Removes a sticky note from a board.

### Save Board

-   Endpoint: `/save_board`
-   Method: POST
-   Description: Stores the current state of a board.

### Fetch User Boards

-   Endpoint: `/fetch_user_boards`
-   Method: GET
-   Description: Retrieves boards for a specific user.

### Savings Opportunities

-   Endpoint: `/savings_opportunities`
-   Method: GET
-   Description: Identifies saving opportunities and association rules for a specific expense category.

### Create Financial Health

-   Endpoint: `/create_financial_health`
-   Method: POST
-   Description: Calculates a financial health score based on various factors and provides personalized tips for improvement.

## Budgets

### Budget Overview

-   Endpoint: `/budget_overview`
-   Method: GET
-   Description: Shows a user's budget overview.

### Delete Budget

-   Endpoint: `/delete_budget`
-   Method: POST
-   Description: Erases a specific budget category.

### Category Budget ViewSet

-   Endpoint: `/category_budgets`
-   Method: CRUD operations
-   Description: Manages category budgets. Allows creating, updating, retrieving, and deleting category budgets. Generates alerts for categories where the user's spending has exceeded their budget limits. Also creates Push Notifications.

## Transactions

### Add Transaction

-   Endpoint: `/add_transaction`
-   Method: POST
-   Description: Creates a new transaction.

### Delete Transaction

-   Endpoint: `/delete_transaction`
-   Method: POST
-   Description: Erases a specific transaction.

### Categories View

-   Endpoint: `/categories_view`
-   Method: GET
-   Description: Retrieves all categories as JSON.

### Manage Categories

-   Endpoint: `/manage_categories`
-   Method: POST
-   Description: Manages categories, including form submissions and creating new ones.

### Delete Category

-   Endpoint: `/delete_category`
-   Method: POST
-   Description: Erases a specific category.

### Transaction List

-   Endpoint: `/transaction_list`
-   Method: GET
-   Description: Displays a list of transactions.

### Transaction Detail

-   Endpoint: `/transaction_detail`
-   Method: GET
-   Description: Shows specific transaction details.

### Forecast Expenses

-   Endpoint: `/forecast_expenses`
-   Method: GET
-   Description: Estimates a user's monthly expenses based on average daily spend.

### Category ViewSet

-   Endpoint: `/categories`
-   Method: CRUD operations
-   Description: Manages categories. Allows creating, updating, retrieving, and deleting categories. Calculates and compares the spending of a user and their friends within a specified category over a given period.

### Transaction ViewSet

-   Endpoint: `/transactions`
-   Method: CRUD operations
-   Description: Manages transactions. Allows creating, updating, retrieving, and deleting transactions. Provides recommendations for transactions based on the user's most frequently used category. Automatically categorizes transactions using keywords in their description and name. Supports creating transactions planned by RecurringTransaction.

## Users

### Signup

-   Endpoint: `/signup`
-   Method: POST
-   Description: Manages user registration.

### User Login

-   Endpoint: `/user_login`
-   Method: POST
-   Description: Handles user sign-in.

### User Logout

-   Endpoint: `/user_logout`
-   Method: POST
-   Description: Manages user sign-out.

### Dashboard

-   Endpoint: `/dashboard`
-   Method: GET
-   Description: Displays the user dashboard.

### User ViewSet

-   Endpoint: `/users`
-   Method: CRUD operations
-   Description: Manages users, user profiles, social media accounts, and friend requests. Allows creating, updating, retrieving, and deleting users and their associated data.

## Capital

### Saving Goal ViewSet

-   Endpoint: `/saving_goals`
-   Method: CRUD operations
-   Description: Manages user-specific saving goals. Supports adding/removing users and categories and ensures the creator's modification rights.

## Database Models

The Financial Management System API utilizes the following database models:

-   Analytics App:
    
    -   StickyNoteContent
    -   StickyNote
    -   Board
    -   BoardStickyNote
-   Capital App:
    
    -   SavingGoal
-   Budgets App:
    
    -   CategoryBudget
-   Transactions App:
    
    -   Category
    -   Transaction
    -   RecurringTransaction
-   Users App:
    
    -   User
    -   UserProfile
    -   SocialMediaAccount
    -   PushNotification
    -   FriendRequest