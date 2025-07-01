# Mirador - Development Blog

A Jekyll-based blog documenting the development of Mirador, a modular, interactive application written in Rust focused on real-time rendering, procedural maze generation, and game-like user interaction.

## About

Mirador is a work-in-progress game engine written entirely in Rust. It leverages modern GPU technologies and immediate-mode GUI frameworks to provide a responsive and visually engaging experience.

Visit the live site: [finitesample.space](https://finitesample.space)

## Development

### Prerequisites

- Ruby 3.4.0 or later
- Bundler gem

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/DetectiveFierce/mirador.git
   cd mirador
   ```

2. Install dependencies:
   ```bash
   bundle install
   ```

3. Run the development server:
   ```bash
   bundle exec jekyll serve
   ```

4. Open your browser to `http://localhost:4000`

### Building for Production

```bash
bundle exec jekyll build
```

The built site will be in the `_site` directory.

## Project Structure

- `_config.yml` - Jekyll configuration
- `_layouts/` - HTML templates
- `_includes/` - Reusable HTML components
- `_posts/` - Blog posts (Markdown)
- `pages/` - Static pages
- `public/` - Static assets (CSS, images, etc.)
- `assets/` - Source assets (fonts, diagrams)

## Content

- **About** - Project overview and architecture
- **App** - Application structure and initialization
- **Game** - Game logic and mechanics
- **Maze** - Procedural maze generation
- **Renderer** - Graphics and rendering pipeline
- **UI** - User interface components
- **Collision** - Collision detection system
- **Blog Posts** - Development updates and technical articles

## License

This project is open source. See the repository for license details.
