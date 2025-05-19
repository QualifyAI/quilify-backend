from typing import Dict, List, Optional
from app.services.learning_path.models import (
    LearningResourceOutput,
    NicheQuestionsOutput, 
    LearningPathOutput,
    DetailedModuleOutput,
    ResourceVerificationOutput,
    LearningModuleOutput,
    SubTopic
)
from app.services.ai.base_ai_service import BaseAIService
from app.models.learning_path import PathQuestion


class LearningPathAIService(BaseAIService):
    """Service for generating AI-based learning paths and related questions"""
    
    async def generate_questions_for_niche(self, niche_name: str) -> List[PathQuestion]:
        """
        Generate multiple choice questions for tailoring a learning path 
        based on the selected niche
        
        Args:
            niche_name: The name of the niche/industry
            
        Returns:
            List of PathQuestion objects with generated questions
        """
        # Create the system prompt
        system_prompt = """
        You are an expert education consultant specializing in personalized learning paths.
        Your task is to create a set of questions that will help tailor a learning journey for
        someone interested in a specific field.
        
        The questions should:
        1. Cover different aspects of the learning experience (experience level, goals, time availability, etc.)
        2. Have multiple choice answer options that represent meaningful distinctions
        3. Help gather information that would meaningfully change how a learning path is structured
        4. Be relevant to the specific field/niche the user is interested in
        
        Each question should have:
        - A unique ID (e.g., 'experience_level', 'primary_goal', 'time_available', etc.)
        - A clear question statement
        - 4-5 distinct answer options
        
        Your questions should help create a truly personalized learning experience.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please generate 5-8 multiple choice questions for a user interested in the "{niche_name}" field.
        
        These questions will be used to customize a learning path specifically for this user based on 
        their experience level, goals, and preferences.
        
        For each question:
        - Create a clear, concise question statement
        - Provide 4-5 distinct answer options that represent different approaches or preferences
        - Ensure the options cover a range of possibilities (beginner to advanced, practical to theoretical, etc.)
        - Make sure the question will provide useful information for customizing a learning journey
        
        Format the response as structured data according to the required schema.
        """
        
        # Make request to Groq
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=NicheQuestionsOutput,
                temperature=0.3
            )
            
            # Convert to PathQuestion model
            return [
                PathQuestion(
                    id=q.id,
                    label=q.label,
                    options=q.options
                ) for q in response.questions
            ]
        except Exception as e:
            # Fall back to generating standard questions
            print(f"Error generating questions with Groq API: {str(e)}")
            return self._generate_fallback_questions(niche_name)
    
    def _generate_fallback_questions(self, niche_name: str) -> List[PathQuestion]:
        """
        Generate fallback questions if API call fails
        
        Args:
            niche_name: The name of the niche/industry
            
        Returns:
            List of standard PathQuestion objects
        """
        return [
            PathQuestion(
                id="experience_level",
                label=f"What is your current experience level in {niche_name}?",
                options=[
                    "Complete beginner with no experience",
                    "Beginner with some basic knowledge",
                    "Intermediate with practical experience",
                    "Advanced with significant experience",
                    "Expert looking to specialize further"
                ]
            ),
            PathQuestion(
                id="learning_goal",
                label=f"What is your primary goal for learning about {niche_name}?",
                options=[
                    "Career transition into this field",
                    "Skill enhancement for current role",
                    "Personal interest and growth",
                    "Academic requirement or research",
                    "Entrepreneurial venture or project"
                ]
            ),
            PathQuestion(
                id="time_commitment",
                label="How much time can you commit to learning each week?",
                options=[
                    "Less than 5 hours",
                    "5-10 hours",
                    "10-20 hours",
                    "20+ hours",
                    "Flexible/variable schedule"
                ]
            ),
            PathQuestion(
                id="learning_style",
                label="What learning approach do you prefer?",
                options=[
                    "Hands-on projects and practical application",
                    "Video courses and tutorials",
                    "Reading books and documentation",
                    "Interactive exercises and quizzes",
                    "Combination of different methods"
                ]
            ),
            PathQuestion(
                id="expertise_focus",
                label=f"Which aspect of {niche_name} are you most interested in?",
                options=[
                    "Fundamental principles and theory",
                    "Practical implementation and tools",
                    "Advanced techniques and specialization",
                    "Industry best practices and standards",
                    "Innovation and emerging trends"
                ]
            )
        ]
    
    async def generate_learning_path(
        self, 
        niche_name: str, 
        answers: Dict[str, str]
    ) -> LearningPathOutput:
        """
        Generate a personalized learning path based on user's niche and question answers
        using an iterative approach that provides deeper, more specific content
        
        Args:
            niche_name: The name of the niche/industry
            answers: Dictionary mapping question IDs to selected answers
            
        Returns:
            LearningPathOutput containing the personalized learning path with detailed modules
        """
        try:
            # Step 1: Generate the high-level learning path framework
            print(f"Generating initial learning path for {niche_name}...")
            initial_path = await self._generate_initial_path(niche_name, answers)
            
            # Step 2: For each module, generate detailed content and resources
            enhanced_modules = []
            
            for i, module in enumerate(initial_path.modules):
                try:
                    print(f"Enhancing module {module.id}: {module.title}...")
                    
                    # Generate detailed content for this module
                    detailed_module = await self._generate_detailed_module(
                        niche_name=niche_name,
                        module=module,
                        user_answers=answers,
                        learning_path_context=initial_path
                    )
                    
                    # Generate verified resources for this module
                    verified_resources = await self._generate_verified_resources(
                        niche_name=niche_name,
                        module_id=module.id,
                        subtopics=[st.title for st in detailed_module.subtopics] if detailed_module.subtopics else module.topics
                    )
                    
                    # Create enhanced module with detailed content and verified resources
                    enhanced_module = LearningModuleOutput(
                        id=module.id,
                        title=module.title,
                        timeline=module.timeline,
                        difficulty=module.difficulty,
                        description=detailed_module.detailedDescription,
                        topics=module.topics,
                        resources=verified_resources.resources,
                        tips=module.tips,
                        subtopics=detailed_module.subtopics,
                        prerequisites=detailed_module.prerequisites,
                        learningObjectives=detailed_module.learningObjectives,
                        projects=detailed_module.projects
                    )
                    
                except Exception as e:
                    print(f"Error enhancing module {module.id}: {str(e)}")
                    # If enhancing a specific module fails, use the original module
                    enhanced_module = module
                
                enhanced_modules.append(enhanced_module)
                print(f"Completed module {module.id} ({i+1}/{len(initial_path.modules)})")
            
            # Return the enhanced learning path with detailed modules
            return LearningPathOutput(
                title=initial_path.title,
                description=initial_path.description,
                estimatedTime=initial_path.estimatedTime,
                modules=enhanced_modules,
                niche=initial_path.niche,
                overview=initial_path.overview,
                prerequisites=initial_path.prerequisites,
                intendedAudience=initial_path.intendedAudience,
                careerOutcomes=initial_path.careerOutcomes
            )
            
        except Exception as e:
            print(f"Error in learning path generation process: {str(e)}")
            # If the entire process fails, create a basic learning path
            return self._create_fallback_learning_path(niche_name, answers)
    
    async def _generate_initial_path(
        self,
        niche_name: str,
        answers: Dict[str, str]
    ) -> LearningPathOutput:
        """
        Generate the initial high-level learning path structure
        
        Args:
            niche_name: The name of the niche/industry
            answers: Dictionary mapping question IDs to selected answers
            
        Returns:
            Basic LearningPathOutput with high-level structure
        """
        # Create the system prompt
        system_prompt = """
        You are an expert education curriculum designer with deep expertise in creating personalized learning paths.
        Your task is to design a comprehensive, structured learning journey for a user based on their specific field
        of interest and their answers to personalization questions.
        
        The learning path you create should:
        1. Be tailored to the user's experience level, goals, and preferences
        2. Follow a logical progression from foundational to advanced concepts
        3. Provide realistic time estimates for each module
        4. Include clear module objectives and topics
        5. Cover both theoretical knowledge and practical applications
        
        In this FIRST PHASE, focus on creating a high-level structure with:
        - A compelling title and description for the overall learning path
        - 4-7 well-structured modules that build upon each other
        - Clear progression and estimated timelines
        - Key topics for each module
        - Basic tips for each module
        
        DO NOT focus on detailed resources or subtopics yet - these will be expanded in the next phase.
        Keep resource links minimal as they will be replaced in a later phase.
        
        Create a compelling, logical learning journey that will take the user from their current level to their goal.
        """
        
        # Format the answers as a readable string
        formatted_answers = "\n".join([f"- {key}: {value}" for key, value in answers.items()])
        
        # Create the user prompt
        user_prompt = f"""
        Please create the high-level framework for a personalized learning path for someone interested in the "{niche_name}" field.
        
        ## USER PROFILE:
        Based on their answers to personalization questions:
        {formatted_answers}
        
        Please design a comprehensive learning path STRUCTURE that:
        - Is tailored specifically to this user's experience level, goals, and preferences
        - Provides a clear progression from fundamentals to advanced concepts
        - Includes 4-7 well-defined modules that build on each other
        - Provides realistic time estimates for completion
        - Includes basic tips for each module
        
        In addition to the standard module information, please also include:
        - An overview of the entire learning journey
        - General prerequisites for the learning path
        - Who the learning path is intended for
        - Potential career outcomes after completion
        
        Remember, this is just the FRAMEWORK. We will expand each module with detailed subtopics and resources in the next step.
        Format the response according to the required schema.
        """
        
        # Make request to Groq
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=LearningPathOutput,
                temperature=0.2
            )
            return response
        except Exception as e:
            # Re-raise with more specific context
            raise Exception(f"Initial learning path generation failed: {str(e)}")
    
    async def _generate_detailed_module(
        self,
        niche_name: str,
        module: LearningModuleOutput,
        user_answers: Dict[str, str],
        learning_path_context: LearningPathOutput
    ) -> DetailedModuleOutput:
        """
        Generate detailed content for a specific module
        
        Args:
            niche_name: The name of the niche/industry
            module: The module to expand
            user_answers: Dictionary mapping question IDs to selected answers
            learning_path_context: The full learning path for context
            
        Returns:
            DetailedModuleOutput with expanded content
        """
        # Create the system prompt
        system_prompt = """
        You are an expert educator and curriculum designer specializing in creating detailed, 
        comprehensive learning modules that help students master complex topics efficiently.
        
        Your task is to expand a high-level learning module into a detailed, structured learning experience.
        You have been provided with a module from a learning path, and you need to create an in-depth 
        breakdown that includes:
        
        1. A detailed description expanding on the initial module description
        2. 3-7 specific subtopics that cover the module content comprehensively
        3. For each subtopic:
           - A clear title
           - A detailed explanation
           - Specific learning resources that are FREE and accessible (with valid links)
        4. Specific prerequisites needed before starting this module
        5. Clear learning objectives (what the learner will be able to do after completing the module)
        6. Hands-on projects or exercises to reinforce learning
        
        For resources, focus EXCLUSIVELY on free, high-quality resources like:
        - Official documentation
        - Free courses (Coursera, edX, etc. that can be audited for free)
        - YouTube tutorials from reputable channels
        - Free eBooks or guides
        - GitHub repositories with learning resources
        - Interactive tutorials and sandboxes
        
        Avoid including any resources that require payment.
        Make sure all links are specific (not generic homepage URLs) and currently active.
        """
        
        # Format user answers for context
        formatted_answers = "\n".join([f"- {key}: {value}" for key, value in user_answers.items()])
        
        # Create a summary of other modules for context
        other_modules = "\n".join([
            f"- Module {m.id}: {m.title} - {m.description}" 
            for m in learning_path_context.modules if m.id != module.id
        ])
        
        # Create the user prompt
        user_prompt = f"""
        Please create a detailed expansion of the following module for a learning path in "{niche_name}".
        
        ## LEARNING PATH CONTEXT:
        - Title: {learning_path_context.title}
        - Description: {learning_path_context.description}
        - Other modules in this path:
        {other_modules}
        
        ## USER PROFILE:
        Based on their answers to personalization questions:
        {formatted_answers}
        
        ## MODULE TO EXPAND:
        - Module ID: {module.id}
        - Title: {module.title}
        - Description: {module.description}
        - Difficulty: {module.difficulty}
        - Topics covered: {', '.join(module.topics)}
        - Timeline: {module.timeline}
        
        ## DETAILED EXPANSION REQUIREMENTS:
        1. Provide an extended, detailed description of this module (at least 3-4 paragraphs)
        
        2. Break down the module into 3-7 subtopics that comprehensively cover the subject matter
           For each subtopic:
           - Clear, specific title
           - Detailed explanation (at least 2 paragraphs)
           - 2-3 specific, FREE learning resources with valid, working links
        
        3. List specific prerequisites needed before starting this module (at least 3-5)
        
        4. Create clear learning objectives for this module (at least 5-7 specific things the learner will be able to do)
        
        5. Suggest 3-5 hands-on projects or exercises to reinforce the learning
        
        Remember to focus EXCLUSIVELY on FREE resources that are currently available and accessible.
        Check that all links work and lead to specific content, not just homepages.
        Format the response according to the required schema.
        """
        
        # Make request to Groq
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=DetailedModuleOutput,
                temperature=0.3
            )
            return response
        except Exception as e:
            # If detailed generation fails, return a basic structure
            print(f"Detailed module generation failed for module {module.id}: {str(e)}")
            
            # Create a basic subtopic from each topic
            basic_subtopics = [
                SubTopic(
                    title=topic,
                    description=f"This subtopic covers {topic} in detail, providing foundational knowledge and practical applications.",
                    resources=[
                        LearningResourceOutput(
                            type="documentation",
                            name=f"Official {topic} Documentation",
                            link=f"https://example.org/{topic.lower().replace(' ', '-')}",
                            description=f"The official documentation for {topic}",
                            isFree=True
                        )
                    ]
                ) for topic in module.topics
            ]
            
            # Return a minimal structure that can be used
            return DetailedModuleOutput(
                moduleId=module.id,
                subtopics=basic_subtopics,
                prerequisites=["Basic understanding of programming concepts"],
                learningObjectives=[f"Understand the fundamentals of {topic}" for topic in module.topics],
                projects=[f"Build a simple project using {module.topics[0]}"],
                detailedDescription=module.description
            )
    
    async def _generate_verified_resources(
        self,
        niche_name: str,
        module_id: int,
        subtopics: List[str]
    ) -> ResourceVerificationOutput:
        """
        Generate verified, free resources for a module
        
        Args:
            niche_name: The name of the niche/industry
            module_id: The ID of the module
            subtopics: List of subtopics to find resources for
            
        Returns:
            ResourceVerificationOutput with verified resources
        """
        # Create the system prompt
        system_prompt = """
        You are an expert curator of educational resources with exceptional knowledge of the best free learning 
        materials available online. Your specialty is finding specific, high-quality, FREE resources that are 
        currently accessible.
        
        Your task is to provide a curated list of educational resources for specific topics that:
        1. Are 100% FREE to access (no paid subscriptions, no "free trials", no limitations)
        2. Have valid, working URLs that lead directly to the specific content
        3. Are high-quality and comprehensive
        4. Are appropriate for the specified learning level
        5. Cover the specified topics thoroughly
        
        For each topic, include diverse resource types:
        - Official documentation
        - Free tutorials (text, video)
        - Interactive learning tools
        - Open courseware from universities
        - GitHub repositories with exercises/examples
        - YouTube channels/playlists from expert educators
        
        Do NOT include:
        - Paid courses or books (even if they're "industry standard")
        - Resources behind paywalls
        - General website homepages without specific content links
        - Outdated or deprecated resources
        - Made-up or generic links
        
        For each resource, provide:
        - Resource type (tutorial, documentation, course, etc.)
        - Specific title
        - Direct, working URL
        - Brief description of what it covers
        - Estimated time to complete (if applicable)
        
        Make sure EVERY link is real, specific, and directly accessible without payment.
        """
        
        # Create the user prompt
        user_prompt = f"""
        Please provide a carefully curated list of FREE learning resources for a module on "{niche_name}" 
        with the following subtopics:
        
        {', '.join(subtopics)}
        
        This is for module ID: {module_id}
        
        Requirements:
        1. Provide at least 10-15 total resources across all the subtopics
        2. EVERY resource must be 100% FREE with no paywalls or subscriptions required
        3. Include a variety of resource types (documentation, tutorials, videos, interactive tools)
        4. Verify that each URL is valid, specific, and works without payment
        5. For each resource, note whether it's for beginners, intermediate, or advanced learners
        6. Focus on resources that are practical and comprehensive
        
        Remember: Quality over quantity. It's better to provide fewer excellent resources than many mediocre ones.
        Double-check all URLs to ensure they lead directly to the specific content, not just to homepages.
        Make all resources truly free, without signup requirements or hidden paywalls.
        Format the response according to the required schema.
        """
        
        # Make request to Groq
        try:
            response = await self._make_groq_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ResourceVerificationOutput,
                temperature=0.4
            )
            return response
        except Exception as e:
            # If resource generation fails, return a basic structure with placeholder resources
            print(f"Resource verification failed for module {module_id}: {str(e)}")
            
            # Create basic resources for each subtopic
            basic_resources = []
            for i, subtopic in enumerate(subtopics):
                # Create 3 resources per subtopic
                basic_resources.extend([
                    LearningResourceOutput(
                        type="documentation",
                        name=f"Official {subtopic} Documentation",
                        link=f"https://developer.mozilla.org/en-US/docs/Web/{subtopic.lower().replace(' ', '_')}",
                        description=f"Comprehensive documentation for {subtopic}",
                        isFree=True,
                        estimatedTime="1-2 hours"
                    ),
                    LearningResourceOutput(
                        type="tutorial",
                        name=f"{subtopic} Tutorial for Beginners",
                        link=f"https://www.freecodecamp.org/news/{subtopic.lower().replace(' ', '-')}-tutorial/",
                        description=f"Step-by-step tutorial on {subtopic} with practical examples",
                        isFree=True,
                        estimatedTime="3-4 hours"
                    ),
                    LearningResourceOutput(
                        type="video",
                        name=f"{subtopic} Crash Course",
                        link=f"https://www.youtube.com/results?search_query={subtopic.lower().replace(' ', '+')}+tutorial",
                        description=f"Video tutorials explaining {subtopic} concepts",
                        isFree=True,
                        estimatedTime="1-2 hours"
                    )
                ])
            
            # Return the basic resources
            return ResourceVerificationOutput(
                moduleId=module_id,
                resources=basic_resources
            )
    
    def _create_fallback_learning_path(self, niche_name: str, answers: Dict[str, str]) -> LearningPathOutput:
        """
        Create a basic fallback learning path when the main generation process fails
        
        Args:
            niche_name: The name of the niche/industry
            answers: Dictionary mapping question IDs to selected answers
            
        Returns:
            Basic LearningPathOutput
        """
        # Extract experience level if available, default to beginner
        experience_level = "beginner"
        for key, value in answers.items():
            if "experience" in key.lower():
                if "advanced" in value.lower() or "expert" in value.lower():
                    experience_level = "advanced"
                elif "intermediate" in value.lower():
                    experience_level = "intermediate"
                break
        
        # Create appropriate modules based on experience level
        modules = []
        
        if experience_level in ["beginner", "intermediate"]:
            # Add fundamentals module for beginners and intermediates
            modules.append(
                LearningModuleOutput(
                    id=1,
                    title=f"{niche_name} Fundamentals",
                    timeline="2-4 weeks",
                    difficulty="Beginner",
                    description=f"Learn the core concepts and fundamentals of {niche_name} to build a solid foundation.",
                    topics=[f"{niche_name} Basics", "Core Concepts", "Fundamental Tools"],
                    resources=[
                        LearningResourceOutput(
                            type="tutorial",
                            name=f"{niche_name} for Beginners",
                            link=f"https://www.freecodecamp.org/news/{niche_name.lower().replace(' ', '-')}-for-beginners/",
                            description=f"Comprehensive tutorial covering {niche_name} basics",
                            isFree=True
                        ),
                        LearningResourceOutput(
                            type="video",
                            name=f"{niche_name} Crash Course",
                            link=f"https://www.youtube.com/results?search_query={niche_name.lower().replace(' ', '+')}+crash+course",
                            description=f"Video tutorial series on {niche_name}",
                            isFree=True
                        ),
                        LearningResourceOutput(
                            type="documentation",
                            name=f"{niche_name} Documentation",
                            link="https://developer.mozilla.org/en-US/docs/Web",
                            description="Official documentation and guides",
                            isFree=True
                        )
                    ],
                    tips=f"Focus on understanding the core principles before moving to more advanced topics."
                )
            )
        
        # Add intermediate module
        modules.append(
            LearningModuleOutput(
                id=len(modules) + 1,
                title=f"Intermediate {niche_name} Concepts",
                timeline="3-6 weeks",
                difficulty="Intermediate",
                description=f"Build on your foundational knowledge with more advanced {niche_name} concepts and practical applications.",
                topics=["Advanced Techniques", "Best Practices", "Common Patterns"],
                resources=[
                    LearningResourceOutput(
                        type="course",
                        name=f"Intermediate {niche_name}",
                        link=f"https://www.freecodecamp.org/learn/{niche_name.lower().replace(' ', '-')}",
                        description=f"Free interactive course on intermediate {niche_name} concepts",
                        isFree=True
                    ),
                    LearningResourceOutput(
                        type="tutorial",
                        name=f"{niche_name} Projects",
                        link=f"https://github.com/topics/{niche_name.lower().replace(' ', '-')}",
                        description=f"Collection of {niche_name} projects on GitHub",
                        isFree=True
                    ),
                    LearningResourceOutput(
                        type="video",
                        name=f"Intermediate {niche_name} Tutorials",
                        link=f"https://www.youtube.com/results?search_query=intermediate+{niche_name.lower().replace(' ', '+')}",
                        description=f"Video tutorials for intermediate {niche_name} learners",
                        isFree=True
                    )
                ],
                tips="Apply what you learn through hands-on projects to solidify your understanding."
            )
        )
        
        # Add advanced module if the user is intermediate or advanced
        if experience_level in ["intermediate", "advanced"]:
            modules.append(
                LearningModuleOutput(
                    id=len(modules) + 1,
                    title=f"Advanced {niche_name} Mastery",
                    timeline="4-8 weeks",
                    difficulty="Advanced",
                    description=f"Master advanced concepts and specialized areas of {niche_name} for professional development.",
                    topics=["Specialized Techniques", "Performance Optimization", "Industry Best Practices"],
                    resources=[
                        LearningResourceOutput(
                            type="course",
                            name=f"Advanced {niche_name} Techniques",
                            link=f"https://www.edx.org/search?q={niche_name.lower().replace(' ', '+')}",
                            description=f"Advanced courses on {niche_name} that can be audited for free",
                            isFree=True
                        ),
                        LearningResourceOutput(
                            type="github",
                            name=f"{niche_name} Advanced Examples",
                            link=f"https://github.com/search?q={niche_name.lower().replace(' ', '+')}+advanced",
                            description=f"Advanced {niche_name} examples and projects on GitHub",
                            isFree=True
                        ),
                        LearningResourceOutput(
                            type="community",
                            name=f"{niche_name} Community Resources",
                            link=f"https://dev.to/t/{niche_name.lower().replace(' ', '')}",
                            description=f"Community articles and discussions on advanced {niche_name} topics",
                            isFree=True
                        )
                    ],
                    tips="Focus on specializing in areas that align with your career goals and interests."
                )
            )
        
        # Add practical application module
        modules.append(
            LearningModuleOutput(
                id=len(modules) + 1,
                title=f"Practical {niche_name} Projects",
                timeline="4-8 weeks",
                difficulty="Varies",
                description=f"Apply your {niche_name} knowledge in real-world projects to build a portfolio and gain practical experience.",
                topics=["Project Planning", "Implementation", "Deployment", "Testing"],
                resources=[
                    LearningResourceOutput(
                        type="project",
                        name=f"{niche_name} Project Ideas",
                        link=f"https://github.com/topics/{niche_name.lower().replace(' ', '-')}-projects",
                        description=f"Collection of {niche_name} project ideas and examples",
                        isFree=True
                    ),
                    LearningResourceOutput(
                        type="tutorial",
                        name="Project-Based Learning Tutorials",
                        link="https://www.freecodecamp.org/news/tag/projects/",
                        description="Step-by-step tutorials for building real projects",
                        isFree=True
                    ),
                    LearningResourceOutput(
                        type="community",
                        name="Open Source Projects",
                        link="https://goodfirstissue.dev/",
                        description="Find beginner-friendly open source projects to contribute to",
                        isFree=True
                    )
                ],
                tips="Build a portfolio of projects that demonstrate your skills and knowledge."
            )
        )
        
        # Create the fallback learning path
        return LearningPathOutput(
            title=f"Comprehensive {niche_name} Learning Path",
            description=f"A structured learning journey to master {niche_name} from fundamentals to advanced topics.",
            estimatedTime=f"{8 + 4 * len(modules)} weeks",
            modules=modules,
            niche=niche_name,
            overview=f"This learning path will guide you through mastering {niche_name}, starting with fundamental concepts and progressing to advanced techniques and practical applications.",
            prerequisites=["Basic computer skills", "Determination to learn", "Regular time commitment"],
            intendedAudience=f"This learning path is designed for individuals interested in learning {niche_name} at their own pace, whether for career development or personal growth.",
            careerOutcomes=[f"{niche_name} Developer", f"{niche_name} Specialist", "Technical Consultant"]
        ) 