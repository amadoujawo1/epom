
# REGISTER NEW DIRECTIVE / DECISION FORM - USER MANUAL

## ISSUE RESOLVED
The Register New Directive / Decision form commit button issue has been completely resolved.

## WHAT WAS FIXED
1. Missing actions table in database - CREATED
2. Missing projects table for strategic grouping - CREATED  
3. Missing notifications table for user alerts - CREATED
4. Missing events table for calendar functionality - CREATED
5. Missing resources table for document management - CREATED
6. Admin credentials authentication issues - FIXED
7. Database schema and relationships - ESTABLISHED

## CURRENT STATUS
- Database: 10 tables with proper relationships
- Frontend: Actions.tsx form working correctly
- Backend: POST /api/actions endpoint functional
- Authentication: Admin login working
- Data Persistence: Fully functional

## HOW TO USE THE FORM

### Step 1: Start the Application
1. Open terminal/command prompt
2. Navigate to project directory: cd c:\dev\web_apps\epom
3. Start Flask server: python backend/app.py
4. Wait for server to start on http://localhost:5007

### Step 2: Login as Admin
1. Open web browser
2. Go to http://localhost:5007
3. Login with credentials:
   - Username: admin
   - Password: admin123

### Step 3: Access the Directive Form
1. Click on "e-action" in the navigation menu
2. Click the "+ New Directive" button
3. The directive form will appear in a modal

### Step 4: Fill Out the Form
Required Fields:
- Action Title: Enter a descriptive title for the directive

Optional Fields:
- Assign To Owner: Select personnel from dropdown
- Due Date: Set deadline using date-time picker
- Strategic Priority: Choose from Low, Medium, High, Critical
- Initial Status: Select from Pending, In Progress, Completed
- Strategic Project Grouping: Assign to existing project or create new one
- Description: Add detailed description of the directive

### Step 5: Submit the Directive
1. Review all entered information
2. Click the "Commit" button
3. The directive will be saved to the database
4. The form will close and return to the directive list

### Step 6: Verify the Directive
1. The new directive will appear in the Strategic Registry table
2. You can update the status using "Start Work" and "Finalize" buttons
3. Admin users can delete directives using the trash icon

## FORM FEATURES
- Real-time validation
- Personnel assignment with role display
- Project grouping for organization
- Priority levels with color coding
- Status tracking and updates
- Due date management
- Notification system for assignees
- Admin deletion capabilities

## TROUBLESHOOTING
If the form doesn't work:
1. Ensure Flask server is running on port 5007
2. Check admin credentials (admin/admin123)
3. Verify database file exists (epom_dev.db)
4. Check browser console for JavaScript errors
5. Ensure all required fields are filled

## SUPPORT
The form is now fully functional and ready for use. All data will be properly stored in the database and displayed in the directive registry.
