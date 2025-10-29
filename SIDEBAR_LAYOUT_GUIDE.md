# Sidebar Layout - Implementation Guide

## ✅ New Layout Implemented!

The Diligence Cloud now features a **left sidebar navigation** with hierarchical project structure, matching your original design vision!

---

## 🎨 New Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│  🅳 Diligence Cloud                        📊 5 Docs  📊 12 Q&A│
├───────────┬────────────────────────────────────────────────────┤
│  PROJECTS │  Q&A Interface  |  Upload Documents               │
│  + New    ├────────────────────────────────────────────────────┤
│           │                                                    │
│ 📁 Acme   │  [Main Content Area with Horizontal Scroll]       │
│   📄 Rev  │                                                    │
│   📄 Risk │                                                    │
│           │                                                    │
│ 📁 Nordic │                                                    │
│           │                                                    │
│ 📁 Lease  │                                                    │
└───────────┴────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### 1. **Left Sidebar (280px wide)**
- Fixed width, doesn't resize
- Contains all projects in tree structure
- Scrollable if many projects
- "+ New" button at top to create projects

### 2. **Project Tree Navigation**
- **Parent Items** - Projects (📁 folder icon)
  - Click to select/activate project
  - Active project highlighted in light blue
  - Blue left border indicates selection

- **Sub-Items** - Documents (📄 document icon)
  - Auto-loaded when project selected
  - Indented with connecting line
  - Shows all documents in project

### 3. **Main Content Area**
- Takes remaining width
- **Horizontal scroll** enabled for table
- Table has `min-width: 1200px` - scrolls if screen < 1200px
- Columns can go beyond screen with scrollbar

### 4. **Responsive Behavior**
- On small screens, sidebar stays fixed
- Content scrolls horizontally
- All columns accessible via scroll

---

## 📐 Layout CSS Architecture

### Container Structure
```css
body {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}

.header { 
    flex-shrink: 0;  /* Fixed height */
}

.main-container {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.sidebar {
    width: 280px;
    flex-shrink: 0;  /* Fixed width */
    overflow-y: auto;
}

.content-area {
    flex: 1;  /* Takes remaining space */
    overflow-x: auto;
    overflow-y: auto;
}
```

### Table Scrolling
```css
.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    min-width: 1200px;  /* Forces scroll if needed */
}
```

---

## 🌳 Project Tree Interactions

### Selecting a Project
```javascript
function selectProject(projectId) {
    // 1. Highlight in sidebar
    // 2. Load project's documents as sub-items
    // 3. Update main content
    // 4. Clear Q&A table
}
```

### Creating a Project
```javascript
function showNewProjectModal() {
    // Shows modal overlay
    // Creates new project
    // Adds to sidebar
    // Auto-selects new project
}
```

### Loading Sub-Items
```javascript
async function loadProjectDocuments(projectId) {
    // Fetches documents for project
    // Displays as sub-items under project
    // Shows 📄 icon for each document
}
```

---

## 🎨 Visual Hierarchy

### Project Item (Parent)
```
📁 Acme Corp
├─ Expandable icon (▶)
├─ Folder icon (📁)
└─ Project name
```

### Sub-Item (Document)
```
   📄 Acme Revenue.pdf
   ├─ Connecting line (CSS ::before)
   ├─ Document icon (📄)
   └─ Document name
```

### Active State
```css
.project-item.active {
    background: #eff6ff;      /* Light blue */
    border-left: 3px solid #667eea;  /* Blue accent */
}
```

---

## 📱 Responsive Design

### Desktop (> 1200px)
```
[ Sidebar 280px ][ Content - All columns visible ]
```

### Laptop (1024px - 1200px)
```
[ Sidebar 280px ][ Content - Scroll for last columns ]
```

### Tablet (768px - 1024px)
```
[ Sidebar 280px ][ Content - Horizontal scroll ]
```

### Mobile (< 768px)
*Future enhancement: Collapsible sidebar*

---

## 🔄 How It Works

### On Page Load:
1. Load all projects from API
2. Display in sidebar tree
3. Select first project automatically
4. Load that project's documents as sub-items
5. Show Q&A interface for that project

### On Project Switch:
1. User clicks different project in sidebar
2. Update active highlight
3. Load new project's documents
4. Clear Q&A table
5. Reload documents tab
6. Update statistics

### On Document Upload:
1. Upload to current selected project
2. Refresh document list
3. Update sub-items in sidebar
4. Update project statistics

---

## 🎯 Example Usage Flow

### Scenario: Working with Multiple Deals

```
1. User opens app
   → Sees "Projects" sidebar with existing projects

2. User clicks "Acme Corp"
   → Sidebar shows:
      📁 Acme Corp (highlighted)
         📄 Financial Statement.pdf
         📄 Investment Memo.pdf
         📄 Legal Contracts.pdf
   → Main area shows Q&A for Acme Corp

3. User uploads new document
   → Document added under Acme Corp folder
   → Sub-items update automatically

4. User clicks "Nordic Telecoms"
   → Sidebar switches highlight
   → Nordic Telecoms documents appear as sub-items
   → Q&A table clears and shows Nordic questions
   → Different context, different data

5. User clicks "+ New"
   → Modal appears
   → Creates "Beta Industries"
   → New folder appears in sidebar
   → Auto-selected
```

---

## 🛠️ Technical Implementation

### HTML Structure
```html
<div class="main-container">
    <!-- Left Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-title">PROJECTS</div>
            <button class="btn-new-project">+ New</button>
        </div>
        <div class="project-tree">
            <!-- Projects loaded here -->
            <div class="project-item active">
                <span class="expand-icon">▶</span>
                <span class="project-icon">📁</span>
                <span class="project-name">Acme Corp</span>
            </div>
            <div class="sub-items visible">
                <div class="sub-item">
                    <span class="sub-icon">📄</span>
                    <span class="sub-name">Revenue.pdf</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Content Area -->
    <div class="content-area">
        <!-- Tabs and content -->
    </div>
</div>
```

### JavaScript State
```javascript
let currentProjectId = null;  // Currently selected project
let projects = [];            // All projects
```

### API Integration
```javascript
// Load projects
GET /api/projects

// Load documents for project
GET /api/documents?project_id={id}

// Upload to project
POST /api/upload?project_id={id}

// Ask question in project context
POST /api/ask { project_id: id, question: "..." }
```

---

## 🎨 Customization Options

### Sidebar Width
```css
.sidebar {
    width: 280px;  /* Change to 240px, 300px, etc. */
}
```

### Sub-Item Indentation
```css
.sub-items {
    padding-left: 28px;  /* Change indent amount */
}
```

### Table Min-Width
```css
table {
    min-width: 1200px;  /* Adjust breakpoint for scroll */
}
```

---

## ✨ Visual Enhancements

### Icons Used
- **📁** Folder icon for projects
- **📄** Document icon for files
- **▶** Expand arrow (rotates to ▼ when expanded)
- **📊** Statistics icons in header

### Color Palette
- **Active Blue**: `#eff6ff` (background), `#667eea` (border)
- **Hover Gray**: `#f9fafb`
- **Border Gray**: `#e5e7eb`
- **Text Dark**: `#374151`
- **Text Light**: `#6b7280`

---

## 🔍 Key Differences from Dropdown

### Before (Dropdown in Header):
```
[Logo] [Dropdown ▼] [Stats]
```

### After (Sidebar):
```
┌─────────┬────────┐
│ PROJECT │ [Logo] │
│ + New   │ [Stats]│
├─────────┼────────┤
│ 📁 Proj │        │
│   📄Doc │ Content│
│ 📁 Proj │        │
└─────────┴────────┘
```

---

## 🚀 Performance Notes

- **Lazy Loading**: Documents loaded only when project selected
- **Efficient Rendering**: Sub-items toggle with CSS (display: none/block)
- **Minimal Re-renders**: Only selected project's sub-items update
- **Smooth Scrolling**: Native browser scrolling in sidebar and content

---

## 🎊 Result

You now have a **professional file-explorer-style interface** with:
- ✅ Left sidebar for project navigation
- ✅ Hierarchical folder/document structure
- ✅ Visual hierarchy with indentation and icons
- ✅ Horizontal scroll for wide tables
- ✅ Clean, modern design matching your vision

**Refresh your browser with `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows) to see the new layout!**

