# Elysia Frontend

![Elysia](./public/logo.svg)

Elysia is a modern AI-powered platform built as a single-page application (SPA) that provides an intuitive interface for AI interactions, data exploration, and configuration management. This frontend application serves as the user interface for the broader Elysia ecosystem.

## 🏗️ Built With

**Framework & Core Technologies:**

- **Next.js 15** - React framework with App Router
- **React 18** - JavaScript library for building user interfaces
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework

**UI Libraries & Components:**

- **Radix UI** - Accessible, unstyled UI primitives
- **Shadcn** - Beautiful & consistent component library
- **Framer Motion** - Production-ready motion library
- **React Markdown** - Markdown component for React
- **React Syntax Highlighter** - Syntax highlighting component

**3D Graphics & Visualization:**

- **Three.js** - 3D graphics library
- **React Three Fiber** - React renderer for Three.js
- **React Three Drei** - Useful helpers for React Three Fiber
- **React Three Postprocessing** - Postprocessing effects

**Data Visualization:**

- **Recharts** - Composable charting library
- **XYFlow React** - Flow chart and node-based UI library

**Development Tools:**

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Cross-env** - Cross-platform environment variables

## 📋 Requirements

- **Node.js** (version 18 or higher)
- **pnpm** (install via `npm install -g pnpm`)
- Modern web browser with ES2017+ support

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd elysia-frontend
   ```

2. **Install dependencies**

   ```bash
   pnpm install
   ```

3. **Start the development server**

   ```bash
   pnpm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
elysia-frontend/
├── app/                          # Next.js app directory
│   ├── api/                      # API route handlers
│   ├── components/               # React components
│   │   ├── chat/                 # Chat-related components
│   │   │   ├── components/       # Shared chat components
│   │   │   ├── displays/         # Various display types
│   │   │   └── nodes/            # Flow node components
│   │   ├── configuration/        # Settings and config components
│   │   ├── contexts/             # React context providers
│   │   ├── debugging/            # Debug tools and utilities
│   │   ├── dialog/               # Modal and dialog components
│   │   ├── evaluation/           # Evaluation and feedback components
│   │   ├── explorer/             # Data exploration components
│   │   ├── navigation/           # Navigation and sidebar components
│   │   └── threejs/              # 3D graphics components
│   ├── pages/                    # Main page components
│   ├── types/                    # TypeScript type definitions
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout component
│   └── page.tsx                  # Homepage component
├── components/                   # Shared UI components
│   └── ui/                       # Reusable UI primitives
├── hooks/                        # Custom React hooks
├── lib/                          # Utility functions
├── public/                       # Static assets
└── configuration files           # Config files (tsconfig, tailwind, etc.)
```

### Key Directories Explained:

- **`app/api/`** - Contains server-side API routes for backend communication
- **`app/components/`** - Core application components organized by feature
- **`app/pages/`** - Main page components (Chat, Data, Settings, etc.)
- **`app/types/`** - TypeScript interfaces and type definitions
- **`components/ui/`** - Reusable UI components built with Radix UI
- **`hooks/`** - Custom React hooks for shared logic
- **`public/`** - Static files like images and icons

## 🎯 Application Features

### Single Page Application (SPA)

Elysia is built as a SPA using Next.js with client-side routing. The main navigation happens through React context (`RouterContext`) without page reloads, providing a smooth user experience.

### Main Sections:

- **Chat** - AI conversation interface
- **Data** - Data exploration and visualization
- **Settings** - Configuration management
- **Evaluation** - AI model evaluation tools
- **Explorer** - Advanced data browsing

### Key Capabilities:

- Real-time chat with AI models
- Interactive data visualizations
- 3D graphics and globe visualizations
- Configurable AI model settings
- Data collection management
- Feedback and evaluation systems

## 🔧 Available Scripts

```bash
# Development
pnpm run dev              # Start development server

# Building
pnpm run build           # Build for production
pnpm run build:clean     # Clean build (removes cache first)

# Export & Assembly
pnpm run export          # Export static files to backend
pnpm run assemble        # Build and export in one command
pnpm run assemble:clean  # Clean build and export

# Other
pnpm start              # Start production server
pnpm run lint           # Run ESLint
```

## 🔨 Build Process

The application uses a custom build process designed for static export:

1. **Build**: Creates an optimized production build
2. **Export**: Generates static files in the `out/` directory
3. **Assembly**: Copies exported files to the backend's static directory

The `export.sh` script handles copying the built static files to `../elysia/api/static` for integration with the backend server.

## 🌐 Environment Configuration

The application supports various environment variables:

- `NEXT_PUBLIC_IS_STATIC` - Enables static export mode

## 🎨 Styling & Theming

- **Tailwind CSS** for utility-first styling
- **CSS Custom Properties** for dynamic theming
- **Custom fonts**: Space Grotesk (text) and Manrope (headings)
- **Responsive design** with mobile-first approach
- **Dark mode support** via CSS classes

## 🧩 Architecture Patterns

- **Context-based state management** for global state
- **Component composition** with Radix UI primitives
- **Custom hooks** for shared logic
- **TypeScript interfaces** for type safety
- **Modular component organization** by feature

## 🌟 Open Source & Contributing

Elysia is an open-source project, and we welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or suggesting enhancements, your contributions help make Elysia better for everyone.

### Ways to Contribute:

- 🐛 **Bug Reports** - Help us identify and fix issues
- ✨ **Feature Requests** - Suggest new functionality
- 💻 **Code Contributions** - Submit pull requests with improvements
- 📚 **Documentation** - Help improve our docs and examples
- 🧪 **Testing** - Help us test new features and report issues

### Contribution Guidelines:

1. **Fork the repository** and create your feature branch
2. **Make your changes** following our coding standards
3. **Ensure all tests pass** and the build is successful
4. **Submit a pull request** with a clear description of your changes

### 🚨 Before Contributing - Build Requirement

**IMPORTANT**: Before submitting any contribution, you MUST ensure that the build process completes successfully:

```bash
pnpm run build
```

This command must run without errors before your pull request will be accepted. This ensures:

- All TypeScript types are valid
- Components render correctly
- Dependencies are properly resolved
- The application can be successfully deployed

If the build fails, please fix all issues before submitting your contribution.

### Getting Help

- Open an issue for bug reports or feature requests
- Join our Weaviate community discussions
- Check out the existing issues for contribution opportunities

We appreciate every contribution, no matter how small. Thank you for helping make Elysia better! 🎉
