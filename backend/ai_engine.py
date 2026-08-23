import os
import json
import random
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Highly accurate, domain-specific offline question bank for Demo Mode
OFFLINE_QUESTION_BANK = {
    "Software Development": {
        "Beginner": [
            {
                "question": "What is the difference between synchronous and asynchronous execution in software development?",
                "expected_answer": "Synchronous execution blocks thread execution until a task completes, running sequentially line-by-line. Asynchronous execution allows tasks to execute concurrently in the background without blocking the main event loop or thread, using callbacks, promises, or async/await syntax.",
                "difficulty": "Beginner"
            },
            {
                "question": "Explain the four core pillars of Object-Oriented Programming (OOP) with real-world analogies.",
                "expected_answer": "The four pillars are: Encapsulation (bundling data and methods while restricting direct state access), Abstraction (hiding complex internal implementation details behind simple public interfaces), Inheritance (reusing attributes/methods from parent classes), and Polymorphism (allowing child classes to provide specialized implementations for shared interface methods).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a RESTful API and what are the standard HTTP methods used?",
                "expected_answer": "REST (Representational State Transfer) is an architectural style for network applications using stateless HTTP requests. Core HTTP methods include GET (retrieve resource), POST (create new resource), PUT (full replacement update), PATCH (partial modification), and DELETE (remove resource).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the difference between Value Types and Reference Types in programming languages?",
                "expected_answer": "Value types (like primitives: int, float, bool) store their actual data directly in memory stack locations. Reference types (like objects, arrays, classes) store a memory address pointer targeting data located on the dynamic heap memory.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Unit Testing and why is Test-Driven Development (TDD) practiced?",
                "expected_answer": "Unit testing verifies individual methods, functions, or modules in total isolation. Test-Driven Development is a practice where developers write failing unit tests first, write minimal code to pass the tests, and then refactor, ensuring high test coverage and regression protection.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain the SOLID principles in Object-Oriented Design and why they promote maintainable code.",
                "expected_answer": "SOLID represents: Single Responsibility (one reason to change), Open/Closed (open for extension, closed for modification), Liskov Substitution (subtypes must be substitutable for base types), Interface Segregation (fine-grained client-specific interfaces), and Dependency Inversion (depend on abstractions, not concrete implementations).",
                "difficulty": "Intermediate"
            },
            {
                "question": "How does memory management work in Python (Reference Counting and Garbage Collection)?",
                "expected_answer": "Python uses reference counting as its primary memory allocation mechanism; when an object's reference counter drops to zero, memory is freed immediately. Cyclic references (where objects reference each other) are detected and deallocated by a background generational garbage collector.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is the difference between Monolithic and Microservices Architecture?",
                "expected_answer": "A Monolith packages all application domain services into a single unified deployment codebase and process. Microservices split the system into autonomous, independently deployable services communicating over lightweight APIs (gRPC/HTTP), enabling independent scaling and fault isolation.",
                "difficulty": "Intermediate"
            },
            {
                "question": "How do Docker containers differ from traditional Virtual Machines (VMs)?",
                "expected_answer": "Containers share the host operating system kernel and isolate processes using Linux namespaces and cgroups, making them lightweight (MBs) and fast to boot. Virtual Machines virtualize full hardware layers, requiring a dedicated guest OS per instance, consuming more memory and CPU.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is CI/CD and how does an automated deployment pipeline work?",
                "expected_answer": "Continuous Integration & Continuous Deployment (CI/CD) automates building, linting, unit testing, image packaging, and deployment whenever code is pushed. It eliminates manual errors, speeds up release cycles, and ensures deployment safety.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "How would you design a distributed rate limiter for a high-throughput API gateway?",
                "expected_answer": "Implement algorithms like Token Bucket or Sliding Window Counter. Store rate limit state in a centralized, low-latency in-memory cache like Redis using atomic Lua scripts to prevent race conditions. Return HTTP status 429 Too Many Requests with retry-after headers when limits are breached.",
                "difficulty": "Advanced"
            },
            {
                "question": "Explain Eventual Consistency vs Strong Consistency in distributed databases under the CAP Theorem.",
                "expected_answer": "The CAP theorem states distributed systems can only guarantee 2 of Consistency, Availability, and Partition Tolerance. Strong consistency guarantees every read receives the most recent write (using consensus like Raft/Paxos). Eventual consistency favors availability, guaranteeing all replicas converge to identical states over time without blocking client reads.",
                "difficulty": "Advanced"
            },
            {
                "question": "What is the N+1 query problem in Object-Relational Mappers (ORMs) and how is it eliminated?",
                "expected_answer": "The N+1 problem occurs when an application executes 1 initial SQL query to fetch N parent records, then triggers N separate SQL queries to fetch child relationships. It is eliminated by Eager Loading (using SQL JOINs or prefetch_related/joinedload in SQLAlchemy/Django).",
                "difficulty": "Advanced"
            }
        ]
    },
    "Artificial Intelligence": {
        "Beginner": [
            {
                "question": "What is Machine Learning and how does Supervised Learning differ from Unsupervised Learning?",
                "expected_answer": "Machine Learning allows systems to learn patterns from data without explicit procedural programming. Supervised learning trains models on labeled input-output pairs (classification/regression). Unsupervised learning discovers latent structures, groupings, or representations in unlabeled data (clustering/dimensionality reduction).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Overfitting in machine learning models and how can it be prevented?",
                "expected_answer": "Overfitting occurs when a model memorizes noise and training data details, performing well on training sets but failing to generalize to unseen test data. Prevention techniques include cross-validation, regularization (L1/L2), dropout, early stopping, data augmentation, and reducing model complexity.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the function of an Activation Function in Neural Networks?",
                "expected_answer": "Activation functions introduce non-linear transformations into network layers, allowing neural networks to learn complex non-linear boundary mappings. Common examples are ReLU (mitigates vanishing gradients), Sigmoid (probability output), and Softmax (multi-class probabilities).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Transformer architecture and how does Self-Attention work?",
                "expected_answer": "Transformers replace sequential recurrent connections (RNNs) with multi-head self-attention mechanisms. Self-attention calculates similarity scores between all tokens in a sequence simultaneously, assigning contextual relevance weights dynamically.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Fine-Tuning in Large Language Models (LLMs)?",
                "expected_answer": "Fine-tuning takes a pre-trained foundation language model and updates its weights on a specialized task-specific dataset (e.g. medical, legal, code) to improve accuracy, domain vocabulary, and instruction adherence.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "What is Retrieval-Augmented Generation (RAG) and why is it preferred over fine-tuning for dynamic knowledge?",
                "expected_answer": "RAG retrieves relevant domain documents from a vector database using semantic similarity search at query time and injects them into the LLM prompt context. It provides verifiable source attribution, reduces hallucinations, and updates knowledge in real-time without expensive model retraining.",
                "difficulty": "Intermediate"
            },
            {
                "question": "Explain the Vanishing and Exploding Gradient problem during backpropagation.",
                "expected_answer": "During deep network backpropagation, repeatedly multiplying small derivative weights causes gradients to vanish to zero (stopping weight updates), while large weights cause gradients to explode to infinity (causing instability). Solutions include residual skip connections (ResNet), layer normalization, ReLU activations, and gradient clipping.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Compare Reinforcement Learning from Human Feedback (RLHF) with Direct Preference Optimization (DPO).",
                "expected_answer": "RLHF trains a separate reward model on human pairwise preferences and uses PPO policy gradient optimization to align LLMs. DPO mathematically reformulates the objective function to directly optimize policy weights on preferred vs dispreferred response pairs without needing a separate reward model or PPO training loop.",
                "difficulty": "Advanced"
            }
        ]
    },
    "Data Science": {
        "Beginner": [
            {
                "question": "What is the standard Data Science Lifecycle from problem definition to deployment?",
                "expected_answer": "The lifecycle includes: Problem Definition -> Data Acquisition -> Data Cleaning & Imputation -> Exploratory Data Analysis (EDA) -> Feature Engineering -> Model Selection & Training -> Validation & Hyperparameter Tuning -> Production Deployment & Monitoring.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the Bias-Variance Tradeoff in statistical modeling?",
                "expected_answer": "Bias is error caused by overly simple assumptions (underfitting). Variance is error caused by extreme sensitivity to small fluctuations in training data (overfitting). Total generalization error is minimized by striking an optimal balance between model complexity and regularization.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Precision, Recall, and the F1-Score in binary classification?",
                "expected_answer": "Precision measures True Positives / (True Positives + False Positives). Recall measures True Positives / (True Positives + False Negatives). F1-Score is the harmonic mean of Precision and Recall, providing a balanced metric for imbalanced datasets.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain the ROC Curve and Area Under the Curve (AUC) metric.",
                "expected_answer": "The Receiver Operating Characteristic (ROC) curve plots True Positive Rate against False Positive Rate across all classification thresholds. AUC measures the entire 2D area beneath the ROC curve; 1.0 represents a perfect classifier and 0.5 represents random guessing.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain how Gradient Boosted Decision Trees (XGBoost/LightGBM) optimize predictive performance.",
                "expected_answer": "Gradient boosting constructs decision trees sequentially, where each new tree is trained to predict the residual pseudo-errors of the preceding ensemble via gradient descent on a specified loss function. XGBoost adds L1/L2 regularization, weighted quantile sketch, and parallelized split finding.",
                "difficulty": "Advanced"
            }
        ]
    },
    "Data Structures": {
        "Beginner": [
            {
                "question": "What is the difference between an Array and a Linked List in memory allocation and time complexity?",
                "expected_answer": "Arrays store elements in contiguous memory blocks allowing O(1) random index access but fixed capacity. Linked Lists store independent nodes with pointers anywhere in dynamic memory, offering O(1) insertion/deletion at known nodes but requiring O(n) sequential traversal.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Stack vs Queue and what are their primary operations?",
                "expected_answer": "A Stack follows Last-In-First-Out (LIFO) order with push() and pop() operations. A Queue follows First-In-First-Out (FIFO) order with enqueue() and dequeue() operations.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Hash Map and how does collision resolution work?",
                "expected_answer": "A Hash Map uses a hash function to map keys to bucket array indices for average O(1) lookups. Collisions (when different keys hash to the same bucket) are resolved using Chaining (linked lists/trees inside buckets) or Open Addressing (linear/quadratic probing).",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain QuickSort vs MergeSort in stability, space complexity, and worst-case time complexity.",
                "expected_answer": "MergeSort is a stable divide-and-conquer algorithm with guaranteed O(n log n) time and O(n) auxiliary space complexity. QuickSort is an unstable in-place algorithm with average O(n log n) time and O(log n) stack space, but degrades to O(n^2) worst-case if pivots are poorly chosen.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain how Red-Black Trees maintain balance during insertion and deletion.",
                "expected_answer": "Red-Black Trees are self-balancing Binary Search Trees where every node is colored red or black. Invariants enforce that root and leaves (NIL) are black, red nodes cannot have red children, and every path from node to leaves contains equal black height. Balancing is maintained via tree rotations and color recoloring in O(log n) time.",
                "difficulty": "Advanced"
            }
        ]
    },
    "Database": {
        "Beginner": [
            {
                "question": "What is the difference between Relational (SQL) and Non-Relational (NoSQL) databases?",
                "expected_answer": "Relational databases (PostgreSQL, MySQL) store data in structured tables with predefined schemas and enforce ACID transactions. NoSQL databases (MongoDB, Redis, Cassandra) store unstructured/semi-structured data (documents, key-value, graphs) and scale horizontally.",
                "difficulty": "Beginner"
            },
            {
                "question": "What are ACID properties in Database Transaction Management?",
                "expected_answer": "ACID stands for Atomicity (all operations complete or roll back), Consistency (data satisfies integrity constraints), Isolation (concurrent transactions do not interfere), and Durability (committed writes persist despite system failure).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Database Indexing and how does B-Tree indexing accelerate queries?",
                "expected_answer": "Database indexing creates auxiliary data structures to quickly locate rows without full table scans. B-Trees maintain balanced search trees where leaf nodes store pointers to table rows, reducing lookup time complexity from O(n) to O(log n).",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "What is Database Sharding and how does Horizontal Partitioning differ from Vertical Partitioning?",
                "expected_answer": "Database Sharding partitions large datasets across independent server nodes using a shard key. Horizontal partitioning splits rows across nodes, while vertical partitioning splits columns into separate physical tables.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain Multi-Version Concurrency Control (MVCC) in PostgreSQL.",
                "expected_answer": "MVCC provides concurrent database access by maintaining multiple tuple versions for each row. Reads do not block writes and writes do not block reads; transactions operate on point-in-time consistent snapshots, with obsolete rows reclaimed by VACUUM processes.",
                "difficulty": "Advanced"
            }
        ]
    },
    "HR": {
        "Beginner": [
            {
                "question": "Tell me about your technical background, core domain expertise, and key project achievements.",
                "expected_answer": "A structured introduction highlighting technical education, primary programming languages/frameworks, significant project impacts, and alignment with target role responsibilities.",
                "difficulty": "Beginner"
            },
            {
                "question": "Describe a scenario where you encountered technical conflict in a team project and how you arrived at a solution.",
                "expected_answer": "Utilize the STAR method (Situation, Task, Action, Result) detailing objective data-driven discussion, active listening, architectural trade-off evaluation, and collaborative resolution.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "How do you manage tight project deadlines or unexpected shifts in technical requirements?",
                "expected_answer": "Explain backlog prioritization, transparent communication with stakeholders, breaking features into MVP deliverables, and maintaining automated test coverage to avoid technical debt.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "How do you handle constructive architectural criticism from senior engineers?",
                "expected_answer": "Emphasize receiving feedback professionally, evaluating alternative proposals objectively against data and benchmarks, and committing fully to team alignment once decisions are finalized.",
                "difficulty": "Advanced"
            }
        ]
    }
}

def generate_questions(
    domain: str,
    difficulty: str,
    num_questions: int = 5,
    resume_skills: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generates highly accurate, domain-specific interview questions using Gemini 1.5 API
    with strict prompts, or falls back to an enriched offline question repository.
    """
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            skills_str = ", ".join(resume_skills) if resume_skills else "Core domain fundamentals"

            prompt = f"""
            You are a Senior Principal Technical Interviewer evaluating candidates for a top-tier software company.
            Domain: {domain}
            Target Difficulty Level: {difficulty}
            Target Candidate Skills: {skills_str}
            Number of Questions Required: {num_questions}

            Instructions for Question Generation:
            1. Formulate exactly {num_questions} highly accurate, realistic, and non-repetitive technical questions.
            2. Questions must match the target difficulty level:
               - Beginner: Precise core principles, fundamental syntax, definitions, and standard use-cases.
               - Intermediate: System design patterns, efficiency, Big-O time/space trade-offs, and error handling.
               - Advanced: Internal mechanics, concurrency/locking, distributed systems, memory models, and scaling bottlenecks.
            3. For each question, provide a comprehensive, authoritative "expected_answer" detailing key technical concepts, mechanics, and reference points.

            Format your response STRICTLY as valid JSON without markdown fences or additional text outside the JSON:
            {{
                "questions": [
                    {{
                        "question": "Detailed technical question here",
                        "expected_answer": "Comprehensive reference answer covering definitions, mechanics, and trade-offs.",
                        "difficulty": "{difficulty}"
                    }}
                ]
            }}
            """

            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            if "questions" in parsed and isinstance(parsed["questions"], list) and len(parsed["questions"]) > 0:
                return parsed["questions"][:num_questions]
        except Exception as e:
            print(f"Gemini API Question Generation notice: {e}. Utilizing enriched offline question repository.")

    # Enriched Offline Demo Mode Fallback
    domain_bank = OFFLINE_QUESTION_BANK.get(domain, OFFLINE_QUESTION_BANK["Software Development"])
    diff_questions = domain_bank.get(difficulty, domain_bank.get("Beginner", []))

    if len(diff_questions) < num_questions:
        all_in_domain = []
        for d_level in ["Beginner", "Intermediate", "Advanced"]:
            all_in_domain.extend(domain_bank.get(d_level, []))
        diff_questions = all_in_domain

    selected = random.sample(diff_questions, min(num_questions, len(diff_questions)))

    while len(selected) < num_questions:
        base = random.choice(diff_questions)
        skill_suffix = f" with practical application to {random.choice(resume_skills)}" if resume_skills else ""
        selected.append({
            "question": f"{base['question'][:-1]}{skill_suffix}?",
            "expected_answer": base["expected_answer"],
            "difficulty": difficulty
        })

    return selected[:num_questions]
