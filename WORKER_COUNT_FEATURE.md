# Worker Count Display on Task Cards

## Summary
Added a prominent worker count badge to each task card that displays the number of workers assigned to that task.

## Changes Made

### 1. Template Update (`templates/tasks.html`)

**Added Worker Count Badge:**
- Located in the footer section of each task card
- Displays the count of workers assigned to the task
- Shows singular "person" or plural "people" based on count
- Positioned in the footer next to the task start date
- Uses an indigo-colored badge design for visual distinction

**Badge Location:**
The badge appears in the footer (bottom) section of the task card, to the right of the "Started on" date information.

### 2. Styling (`templates/tasks.html` - CSS section)

**New CSS Classes:**
- `.worker-count-badge` - Main styling for the badge
  - Gradient background (indigo colors)
  - Subtle shadow for depth
  - Smooth transitions
  - Hover effects with scale animation
  - Enhanced shadow on task card hover

**Features:**
- **Hover Effect:** The badge slightly scales up and increases shadow when you hover over it
- **Interactive:** When the entire task card is hovered, the badge scales up further for better visibility
- **Responsive:** Works seamlessly with the existing task card design
- **Accessible:** Clear numbers with readable font weight and color contrast

## Design Details

### Badge Design:
```
┌─────────────┐
│   Count     │
│  (in bold)  │
│   unit      │
└─────────────┘
```

Example:
- Single worker: Shows "1" with "person"
- Multiple workers: Shows "5" with "people"

### Colors:
- **Background Gradient:** Indigo (#818cf8 to #6366f1)
- **Text:** Bold indigo (#4f46e5)
- **Border:** Indigo border for definition
- **Shadow:** Indigo-tinted shadow for depth

## Code Implementation

### Template Code:
```html
<!-- Worker Count Badge -->
<div class="flex items-center">
    <div class="worker-count-badge flex-shrink-0 w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center border-2 border-indigo-300">
        <div class="flex flex-col items-center justify-center">
            <div class="text-lg font-bold text-indigo-600">{{ task.workers.count() }}</div>
            <div class="text-xs text-indigo-600 font-medium">
                {% if task.workers.count() == 1 %}
                    person
                {% else %}
                    people
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

### CSS Code:
```css
/* Worker count badge styling */
.worker-count-badge {
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    transition: all 0.3s ease;
}

.worker-count-badge:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.task-card:hover .worker-count-badge {
    transform: scale(1.08);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
}
```

## How It Works

1. **Data Source:** Uses the Task model's `workers` relationship (many-to-many relationship defined in models.py)
2. **Count Method:** Uses the `.count()` method on the SQLAlchemy query object
3. **Dynamic Text:** Automatically pluralizes between "person" and "people" based on the count
4. **Real-time:** Updates whenever workers are added to or removed from a task

## User Experience

**Visual Feedback:**
- Users can immediately see how many workers are assigned to each task without clicking
- The badge stands out visually with its indigo gradient
- Smooth animations on hover provide interactive feedback
- Clear, readable typography ensures the count is easily visible

**Information Hierarchy:**
- Badge is positioned in the footer where users naturally look for summary information
- Large, bold number for quick scanning
- Semantic label ("person/people") for clarity

## Benefits

1. **Quick Overview:** See team size at a glance
2. **Planning:** Helps identify which tasks have adequate staffing
3. **Tracking:** Easy to spot tasks with no workers assigned
4. **Visual Design:** Adds visual interest while providing useful information
5. **Mobile-Friendly:** Badge adapts well to different screen sizes

## Testing Recommendations

1. **Verification:**
   - Create a task with no workers → should show "0 people"
   - Add 1 worker to a task → should show "1 person"
   - Add multiple workers → should show "X people" (plural)

2. **Visual Testing:**
   - Hover over the badge → verify scale effect
   - Hover over task card → verify badge scales more
   - Check on different screen sizes (mobile, tablet, desktop)

3. **Performance:**
   - Verify count updates when workers are added/removed without page refresh
   - Check that query is efficient for tasks with many workers

## Future Enhancements

1. **Click to View Workers:** Make the badge clickable to view assigned workers
2. **Worker Avatars:** Show small avatar thumbnails in the badge
3. **Presence Indicators:** Color code badge based on active/inactive workers
4. **Status Breakdown:** Show breakdown by attendance status (e.g., "5 assigned, 3 present")
5. **Pagination:** If many workers, show "5+ people" with tooltip showing full list
