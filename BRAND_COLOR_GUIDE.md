# Brand Color Usage Guide

## Quick Reference

### Primary Actions (Buttons, Links, Headers)
Use **brand-navy** for all primary interactive elements:

```html
<!-- Primary Buttons -->
<button class="btn bg-brand-navy-500 hover:bg-brand-navy-600 text-white">
  Click Me
</button>

<!-- Primary Links -->
<a href="#" class="text-brand-navy-600 hover:text-brand-navy-700">
  Learn More
</a>

<!-- Headers/Titles -->
<h1 class="text-brand-navy-700">Dashboard</h1>
<h2 class="text-brand-navy-600">Section Title</h2>
```

### Backgrounds & Cards
Use lighter shades of brand-navy for backgrounds:

```html
<!-- Light background panels -->
<div class="bg-brand-navy-50 border border-brand-navy-200">
  Content here
</div>

<!-- Gradient headers -->
<div class="bg-gradient-to-r from-brand-navy-500 to-brand-navy-600">
  <h2 class="text-white">Header</h2>
</div>

<!-- Hover states -->
<div class="hover:bg-brand-navy-50 transition-colors">
  Hoverable content
</div>
```

### Accent & Highlights
Use **brand-gold** for special elements, badges, and highlights:

```html
<!-- Success badges -->
<span class="badge bg-brand-gold-100 text-brand-gold-700">
  New
</span>

<!-- Premium features -->
<div class="border-l-4 border-brand-gold-500 bg-brand-gold-50 p-4">
  <p class="text-brand-gold-800">Premium Feature</p>
</div>

<!-- Important highlights -->
<div class="bg-brand-gold-100 text-brand-gold-800 rounded-lg p-3">
  <i class="fas fa-star text-brand-gold-600"></i>
  Featured Item
</div>
```

### Neutral Text & Borders
Use **brand-gray** for body text and subtle elements:

```html
<!-- Body text -->
<p class="text-brand-gray-700">Regular paragraph text</p>
<p class="text-brand-gray-500">Secondary text</p>

<!-- Borders & dividers -->
<div class="border border-brand-gray-200">Content</div>
<hr class="border-brand-gray-300" />

<!-- Subtle backgrounds -->
<div class="bg-brand-gray-50">
  Light background
</div>
```

## Color Shade Guide

### When to use each shade:

#### 50-100: Very Light (Backgrounds, Hover States)
- `brand-navy-50`: Lightest background, hover states
- `brand-navy-100`: Light background panels, subtle highlights

#### 200-300: Light (Borders, Disabled States)
- `brand-navy-200`: Borders, input borders
- `brand-navy-300`: Darker borders, disabled text

#### 400-500: Medium (Icons, Secondary Text)
- `brand-navy-400`: Icons, placeholder text
- `brand-navy-500`: **Primary brand color**, main buttons

#### 600-700: Dark (Primary Text, Hover States)
- `brand-navy-600`: Button hover states, darker headers
- `brand-navy-700`: Primary text, important headers

#### 800-900: Very Dark (Emphasis, Contrast)
- `brand-navy-800`: Strong emphasis text
- `brand-navy-900`: Maximum contrast text

## Common Patterns

### Form Inputs
```html
<input 
  type="text" 
  class="border-brand-navy-200 
         focus:border-brand-navy-500 
         focus:ring-brand-navy-200
         bg-white
         hover:bg-brand-navy-50"
/>
```

### Cards with Headers
```html
<div class="bg-white rounded-lg shadow-lg overflow-hidden">
  <!-- Header -->
  <div class="bg-gradient-to-r from-brand-navy-500 to-brand-navy-600 p-4">
    <h3 class="text-white font-bold">Card Title</h3>
    <p class="text-brand-navy-100 text-sm">Description</p>
  </div>
  
  <!-- Body -->
  <div class="p-6">
    <p class="text-brand-gray-700">Card content goes here</p>
  </div>
</div>
```

### Alerts & Notifications
```html
<!-- Info Alert -->
<div class="bg-brand-navy-50 border-l-4 border-brand-navy-500 p-4">
  <div class="flex items-center">
    <i class="fas fa-info-circle text-brand-navy-600 mr-3"></i>
    <p class="text-brand-navy-800">Important information</p>
  </div>
</div>

<!-- Success Alert -->
<div class="bg-brand-gold-50 border-l-4 border-brand-gold-500 p-4">
  <div class="flex items-center">
    <i class="fas fa-check-circle text-brand-gold-600 mr-3"></i>
    <p class="text-brand-gold-800">Action completed successfully</p>
  </div>
</div>
```

### Badges & Tags
```html
<!-- Primary Badge -->
<span class="badge bg-brand-navy-500 text-white">Active</span>

<!-- Secondary Badge -->
<span class="badge bg-brand-gray-200 text-brand-gray-700">Pending</span>

<!-- Accent Badge -->
<span class="badge bg-brand-gold-100 text-brand-gold-700">Featured</span>
```

## Gradients

### Primary Gradients
```html
<!-- Navy gradient (headers, hero sections) -->
<div class="bg-gradient-to-r from-brand-navy-500 to-brand-navy-600"></div>

<!-- Navy gradient with slate (subtle variation) -->
<div class="bg-gradient-to-br from-brand-navy-500 to-slate-600"></div>

<!-- Light navy gradient (backgrounds) -->
<div class="bg-gradient-to-br from-brand-navy-50 to-brand-navy-100"></div>
```

### Accent Gradients
```html
<!-- Gold accent gradient -->
<div class="bg-gradient-to-r from-brand-gold-400 to-brand-gold-500"></div>

<!-- Subtle gold background -->
<div class="bg-gradient-to-br from-brand-gold-50 to-brand-gold-100"></div>
```

## Accessibility

### Ensure Proper Contrast
- **Body text**: Use brand-gray-700 or darker on white backgrounds
- **Headers**: Use brand-navy-700 or darker on white backgrounds
- **Links**: Use brand-navy-600 with hover:brand-navy-700
- **Buttons**: White text on brand-navy-500 (or darker) backgrounds

### Test Color Combinations
Good combinations:
- White text on brand-navy-500+ ✓
- brand-navy-700 text on white background ✓
- brand-navy-800 text on brand-navy-50 background ✓
- brand-gold-800 text on brand-gold-50 background ✓

Avoid:
- Light text on light backgrounds ✗
- Dark text on dark backgrounds ✗
- brand-navy-300 text on white (low contrast) ✗

## Migration Tips

### Replacing Old Colors

#### Old Indigo/Blue → New Brand Navy
```html
<!-- OLD -->
<button class="bg-indigo-600 hover:bg-indigo-700">Click</button>
<h1 class="text-blue-700">Title</h1>

<!-- NEW -->
<button class="bg-brand-navy-600 hover:bg-brand-navy-700">Click</button>
<h1 class="text-brand-navy-700">Title</h1>
```

#### Adding Accent Colors
```html
<!-- Add gold for special features -->
<div class="border-l-4 border-brand-gold-500">
  <span class="text-brand-gold-800">Premium</span>
</div>
```

## Examples from Your App

### Reports Page Header
```html
<div class="bg-gradient-to-r from-brand-navy-500 to-brand-navy-600 p-6">
  <h2 class="text-white font-bold">Report Date Range</h2>
  <p class="text-brand-navy-100">Configure the time period</p>
</div>
```

### Date Input
```html
<input 
  type="text" 
  class="border-brand-navy-200 
         focus:border-brand-navy-500 
         focus:ring-brand-navy-200
         hover:bg-brand-navy-50"
/>
```

### Action Buttons
```html
<button class="btn bg-brand-navy-600 hover:bg-brand-navy-700 text-white">
  Download Report
</button>
```

## Quick Color Picker

Copy and paste these classes:

**Backgrounds:**
- `bg-brand-navy-50` `bg-brand-navy-100` `bg-brand-navy-500` `bg-brand-navy-600`
- `bg-brand-gold-50` `bg-brand-gold-100` `bg-brand-gold-500`
- `bg-brand-gray-50` `bg-brand-gray-100`

**Text:**
- `text-brand-navy-600` `text-brand-navy-700` `text-brand-navy-800`
- `text-brand-gold-600` `text-brand-gold-700` `text-brand-gold-800`
- `text-brand-gray-600` `text-brand-gray-700` `text-brand-gray-800`

**Borders:**
- `border-brand-navy-200` `border-brand-navy-300` `border-brand-navy-500`
- `border-brand-gold-200` `border-brand-gold-300`
- `border-brand-gray-200` `border-brand-gray-300`
