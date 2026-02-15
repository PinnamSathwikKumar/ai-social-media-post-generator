import openai
from config import Config
import json

class AIGenerator:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Using fallback generator.")
    
    def generate_post(self, event_data, platform, tone):
        if Config.OPENAI_API_KEY:
            return self._generate_with_openai(event_data, platform, tone)
        else:
            return self._generate_fallback(event_data, platform, tone)
    
    def _generate_with_openai(self, event_data, platform, tone):
        """Generate post using OpenAI API"""
        try:
            # Create client with only api_key parameter
            # This avoids any proxy-related issues
            client_kwargs = {'api_key': Config.OPENAI_API_KEY}
            client = openai.OpenAI(**client_kwargs)
            
            prompt = self._build_prompt(event_data, platform, tone)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content creator expert. Generate engaging, platform-appropriate social media posts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=250
            )
            
            result = response.choices[0].message.content
            
            content, hashtags = self._parse_response(result, platform)
            
            return {
                'content': content,
                'hashtags': hashtags
            }
        except TypeError as e:
            # Handle version compatibility issues
            if 'proxies' in str(e) or 'unexpected keyword argument' in str(e):
                print(f"OpenAI library version compatibility issue: {e}")
                print("Falling back to template-based generator. Consider updating openai library: pip install --upgrade openai")
            else:
                print(f"Error generating with OpenAI: {e}")
            return self._generate_fallback(event_data, platform, tone)
        except Exception as e:
            print(f"Error generating with OpenAI: {e}")
            return self._generate_fallback(event_data, platform, tone)
    
    def _build_prompt(self, event_data, platform, tone):
        """Build prompt for AI generation"""
        platform_guidelines = {
            'linkedin': 'Professional tone, business-focused, 1300 characters max, include relevant industry hashtags',
            'instagram': 'Visual and engaging, use emojis, 2200 characters max, include trending hashtags (5-10)',
            'facebook': 'Conversational and community-focused, 5000 characters max, include relevant hashtags',
            'twitter': 'Concise and engaging, 280 characters max, use 1-3 relevant hashtags'
        }
        
        tone_guidelines = {
            'formal': 'Use formal language, professional terminology',
            'professional': 'Use professional but approachable language',
            'promotional': 'Use persuasive language, highlight benefits and value',
            'friendly': 'Use casual, warm, and approachable language'
        }
        
        prompt = f"""Generate a {tone} social media post for {platform}.

Event Details:
- Title: {event_data.get('title', 'N/A')}
- Date: {event_data.get('date', 'N/A')}
- Location: {event_data.get('location', 'N/A')}
- Type: {event_data.get('type', 'N/A')}
- Description: {event_data.get('description', 'N/A')}

Platform Guidelines: {platform_guidelines.get(platform, '')}
Tone Guidelines: {tone_guidelines.get(tone, '')}

Please generate:
1. A compelling caption/post content
2. Relevant hashtags (separated by spaces, starting with #)

Format your response as:
CONTENT:
[your post content here]

HASHTAGS:
[hashtags here, each starting with #]
"""
        return prompt
    
    def _parse_response(self, response_text, platform):
        """Parse AI response to extract content and hashtags"""
        try:
            lines = response_text.split('\n')
            content_lines = []
            hashtags = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if 'CONTENT:' in line.upper():
                    current_section = 'content'
                    continue
                elif 'HASHTAGS:' in line.upper():
                    current_section = 'hashtags'
                    continue
                
                if current_section == 'content' and line:
                    content_lines.append(line)
                elif current_section == 'hashtags' and line:
                    # Extract hashtags
                    words = line.split()
                    for word in words:
                        if word.startswith('#'):
                            hashtags.append(word)
            
            content = '\n'.join(content_lines).strip()
            hashtags_str = ' '.join(hashtags) if hashtags else self._generate_default_hashtags(platform)
            
            # If parsing failed, use the whole response as content
            if not content:
                content = response_text.strip()
                hashtags_str = self._generate_default_hashtags(platform)
            
            return content, hashtags_str
        except Exception as e:
            print(f"Error parsing response: {e}")
            return response_text.strip(), self._generate_default_hashtags(platform)
    
    def _generate_fallback(self, event_data, platform, tone):
        """Fallback generator when AI API is not available"""
        title = event_data.get('title', 'Event')
        date = event_data.get('date', '')
        location = event_data.get('location', '')
        event_type = event_data.get('type', '')
        description = event_data.get('description', '')
        
        # Platform-specific templates
        if platform == 'twitter':
            content = f"🎉 {title}\n\n📅 {date}"
            if location:
                content += f"\n📍 {location}"
            content += f"\n\n{description[:200]}"
        elif platform == 'linkedin':
            content = f"We're excited to announce: {title}\n\n"
            content += f"📅 Date: {date}\n"
            if location:
                content += f"📍 Location: {location}\n"
            content += f"\n{description}\n\nJoin us for this {event_type} event!"
        elif platform == 'instagram':
            content = f"✨ {title} ✨\n\n"
            content += f"📅 {date}\n"
            if location:
                content += f"📍 {location}\n"
            content += f"\n{description}\n\nDon't miss out! 🎉"
        else:  # facebook
            content = f"Join us for {title}!\n\n"
            content += f"📅 Date: {date}\n"
            if location:
                content += f"📍 Location: {location}\n"
            content += f"\n{description}\n\nWe hope to see you there!"
        
        hashtags = self._generate_default_hashtags(platform)
        
        return {
            'content': content,
            'hashtags': hashtags
        }
    
    def _generate_default_hashtags(self, platform):
        """Generate default hashtags based on platform"""
        base_hashtags = ['#Event', '#Community', '#Networking']
        
        if platform == 'instagram':
            return ' '.join(base_hashtags + ['#EventPlanning', '#SocialEvent', '#JoinUs'])
        elif platform == 'linkedin':
            return ' '.join(base_hashtags + ['#ProfessionalDevelopment', '#BusinessEvent'])
        elif platform == 'twitter':
            return ' '.join(base_hashtags[:2])  # Shorter for Twitter
        else:
            return ' '.join(base_hashtags)

