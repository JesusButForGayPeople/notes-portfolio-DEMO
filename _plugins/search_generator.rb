module Jekyll
  class SearchGenerator < Generator
    safe true
    priority :normal

    def strip_html_tags(text)
      text.to_s.gsub(/<[^>]*>/, '').strip
    end

    def generate_excerpt(content, search_terms = [])
      return content.split[0..49].join(" ") + "..." if search_terms.empty?
      
      content_lower = content.downcase
      best_position = 0
      best_score = 0
      
      # Find the best position that contains the most search terms
      search_terms.each do |term|
        term_lower = term.downcase
        pos = content_lower.index(term_lower)
        if pos
          # Calculate a score based on how many terms are near this position
          score = 0
          search_terms.each do |other_term|
            other_pos = content_lower.index(other_term.downcase, [pos - 100, 0].max)
            if other_pos && (other_pos - pos).abs < 200
              score += 1
            end
          end
          
          if score > best_score
            best_score = score
            best_position = pos
          end
        end
      end
      
      # Extract context around the best position
      start_pos = [best_position - 100, 0].max
      end_pos = [best_position + 200, content.length].min
      
      excerpt = content[start_pos..end_pos]
      
      # Clean up the excerpt
      excerpt = excerpt.strip
      
      # Add ellipsis if we're not at the beginning
      excerpt = "..." + excerpt if start_pos > 0
      
      # Add ellipsis if we're not at the end
      excerpt = excerpt + "..." if end_pos < content.length
      
      # Ensure the excerpt isn't too long
      if excerpt.length > 300
        excerpt = excerpt[0..297] + "..."
      end
      
      excerpt
    end

    def generate(site)
      search_data = []

      # Add blog posts
      site.posts.docs.each do |post|
        content = strip_html_tags(post.content)
        excerpt = strip_html_tags(post.data["excerpt"] || generate_excerpt(content))
        
        search_data << {
          "title" => post.data["title"],
          "url" => post.url,
          "excerpt" => excerpt,
          "type" => "Blog Post",
          "date" => post.date.strftime("%B %d, %Y"),
          "content" => content
        }
      end

      # Add pages
      site.pages.each do |page|
        next if page.url == "/search/" || page.data["layout"] != "page"
        
        content = strip_html_tags(page.content)
        excerpt = strip_html_tags(generate_excerpt(content))
        
        search_data << {
          "title" => page.data["title"],
          "url" => page.url,
          "excerpt" => excerpt,
          "type" => "Page",
          "date" => nil,
          "content" => content
        }
      end

      # Create the search.json file
      site.pages << SearchPage.new(site, search_data)
    end
  end

  class SearchPage < Page
    def initialize(site, search_data)
      @site = site
      @base = site.source
      @dir = ""
      @name = "search.json"

      self.process(@name)
      self.data = {}
      self.content = search_data.to_json
    end

    def render(layouts, site_payload)
      self.content
    end
  end
end 