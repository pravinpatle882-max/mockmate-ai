import os
import json
import random
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Local offline question bank for Demo Mode fallback
OFFLINE_QUESTION_BANK = {
    "Software Development": {
        "Beginner": [
            {
                "question": "What is the difference between synchronous and asynchronous execution in programming?",
                "expected_answer": "Synchronous execution blocks the thread until a task finishes, executing line by line sequentially. Asynchronous execution allows tasks to run concurrently in the background without blocking the main event loop or main thread.",
                "difficulty": "Beginner"
            },
            {
                "question": "Explain the concept of Object-Oriented Programming (OOP) and its key pillars.",
                "expected_answer": "OOP is a programming paradigm based on objects containing data and methods. Its core pillars are Encapsulation (hiding internal state), Abstraction (simplifying interface), Inheritance (reusing code across classes), and Polymorphism (overriding methods dynamically).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Version Control and why is Git widely used in software development?",
                "expected_answer": "Version control tracks and manages changes to software code over time. Git is a distributed version control system that allows multiple developers to branch, merge, track history, and collaborate efficiently without clashing.",
                "difficulty": "Beginner"
            },
            {
                "question": "What are RESTful APIs and what are the standard HTTP methods used?",
                "expected_answer": "REST (Representational State Transfer) is an architectural style for network applications using stateless HTTP requests. Key methods are GET (read data), POST (create resource), PUT/PATCH (update resource), and DELETE (remove resource).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is unit testing and why is it important during development?",
                "expected_answer": "Unit testing tests individual functions, modules, or classes in isolation. It catches bugs early in the development lifecycle, ensures refactoring safety, and verifies core business logic functions as expected.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain SOLID principles in Object-Oriented Design.",
                "expected_answer": "SOLID stands for: Single Responsibility Principle, Open/Closed Principle, Liskov Substitution Principle, Interface Segregation Principle, and Dependency Inversion Principle. They ensure clean, extensible, and maintainable software architecture.",
                "difficulty": "Intermediate"
            },
            {
                "question": "How does memory management work in Python (garbage collection & reference counting)?",
                "expected_answer": "Python uses reference counting as its primary memory management mechanism. When an object's reference count drops to zero, memory is deallocated. Cyclic references are handled by a generational garbage collector.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is the difference between monolithic architecture and microservices architecture?",
                "expected_answer": "A monolith bundles all application services into a single unified codebase and deployment artifact. Microservices decompose the system into small, independently deployable services communicating over APIs, enhancing scalability and isolation.",
                "difficulty": "Intermediate"
            },
            {
                "question": "How do Docker containers differ from traditional Virtual Machines (VMs)?",
                "expected_answer": "Docker containers share the host operating system kernel and isolate applications at the process level, making them lightweight and fast. VMs virtualize complete hardware with full OS instances, requiring more resources and startup time.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is CI/CD and how does a automated pipeline benefit software delivery?",
                "expected_answer": "Continuous Integration & Continuous Deployment (CI/CD) automates building, testing, and deploying software. It enables frequent, reliable code updates, reduces human errors, and speeds up time-to-market.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "How would you design a rate-limiting system for a high-traffic microservices API?",
                "expected_answer": "Use algorithms like Token Bucket, Leaky Bucket, or Fixed/Sliding Window Log. Store rate limit counters in distributed, low-latency in-memory databases like Redis with atomic operations, and return HTTP 429 Too Many Requests when limits are exceeded.",
                "difficulty": "Advanced"
            },
            {
                "question": "Explain Eventual Consistency vs Strong Consistency in distributed systems (CAP Theorem).",
                "expected_answer": "Under CAP theorem, distributed systems choose between Consistency, Availability, and Partition Tolerance. Strong consistency guarantees all nodes read the latest write immediately (e.g. 2-phase commit). Eventual consistency guarantees that all replicas will converge given time without blocking writes.",
                "difficulty": "Advanced"
            },
            {
                "question": "What is the N+1 query problem in ORMs and how do you resolve it?",
                "expected_answer": "The N+1 problem occurs when an application executes 1 initial query to fetch N parent records, then N separate queries to fetch related child records. It is resolved using Eager Loading (JOINs or prefetching relationships in SQLAlchemy/Django ORM).",
                "difficulty": "Advanced"
            }
        ]
    },
    "Artificial Intelligence": {
        "Beginner": [
            {
                "question": "What is Artificial Intelligence and how does Machine Learning differ from traditional programming?",
                "expected_answer": "AI is the broad field of creating systems capable of human-like intelligence. Traditional programming uses explicit rules and input data to produce output, while Machine Learning feeds input data and desired outputs into algorithms to automatically learn patterns and rules.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Supervised Learning vs Unsupervised Learning?",
                "expected_answer": "Supervised learning trains models on labeled dataset pairs (inputs and target answers), like classification and regression. Unsupervised learning finds hidden patterns, clusters, or representations in unlabeled data, like K-Means clustering.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Overfitting in machine learning models and how can it be prevented?",
                "expected_answer": "Overfitting happens when a model learns noise and specific details of the training data too closely, failing to generalize to unseen test data. It is prevented using cross-validation, regularization (L1/L2), dropout, pruning, and collecting more training data.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the purpose of an Activation Function in Artificial Neural Networks?",
                "expected_answer": "Activation functions introduce non-linearity into neural network layers, enabling the network to learn complex non-linear relationships. Popular examples include ReLU, Sigmoid, and Softmax.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Large Language Model (LLM) fine-tuning?",
                "expected_answer": "Fine-tuning takes a pre-trained general language model and further trains it on a specific domain dataset (e.g., medical, legal, code) to improve performance on specialized tasks.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain the Transformer architecture and the Self-Attention mechanism.",
                "expected_answer": "Transformers rely on multi-head self-attention mechanisms to compute dependencies between all tokens in a sequence simultaneously without sequential recurrence (RNNs). Attention weights calculate how relevant each token is to every other token.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is Retrieval-Augmented Generation (RAG) and why is it useful for LLM applications?",
                "expected_answer": "RAG combines vector databases with LLMs to retrieve relevant external domain documents at query time and feed them as context to the model, reducing hallucinations and providing up-to-date domain knowledge without re-training.",
                "difficulty": "Intermediate"
            },
            {
                "question": "Explain the Vanishing and Exploding Gradient problem in Deep Neural Networks.",
                "expected_answer": "During backpropagation through many layers, gradients multiplied repeatedly can diminish to zero (vanishing) or blow up to infinity (exploding). Solutions include ReLU activations, residual connections (ResNet), layer normalization, and gradient clipping.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Compare Reinforcement Learning from Human Feedback (RLHF) vs Direct Preference Optimization (DPO).",
                "expected_answer": "RLHF uses a reward model trained on human rankings combined with PPO optimization to align LLMs. DPO simplifies this by directly optimizing the policy model on preferred vs dispreferred text pairs without needing a separate reward model or complex PPO training loop.",
                "difficulty": "Advanced"
            },
            {
                "question": "How do Vector Embeddings and Cosine Similarity function in Semantic Search?",
                "expected_answer": "Vector embeddings project text into continuous high-dimensional vector spaces where semantic similarity corresponds to vector proximity. Cosine similarity calculates the dot product divided by the product of vector norms, measuring directional alignment regardless of magnitude.",
                "difficulty": "Advanced"
            }
        ]
    },
    "Data Science": {
        "Beginner": [
            {
                "question": "What is the Data Science Lifecycle and what are its key stages?",
                "expected_answer": "The lifecycle includes Problem Definition, Data Collection, Data Cleaning & Preprocessing, Exploratory Data Analysis (EDA), Feature Engineering, Model Training & Evaluation, and Deployment.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the difference between Mean, Median, and Mode?",
                "expected_answer": "Mean is the arithmetic average of all numbers. Median is the middle value in a sorted dataset (robust to outliers). Mode is the most frequently occurring value in the dataset.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is the Bias-Variance Tradeoff in machine learning?",
                "expected_answer": "Bias is error introduced by oversimplifying assumptions (underfitting). Variance is error from sensitivity to small fluctuations in training data (overfitting). Total error is minimized by finding the optimal balance between bias and variance.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Precision vs Recall and what is the F1-Score?",
                "expected_answer": "Precision is True Positives / (True Positives + False Positives). Recall is True Positives / (True Positives + False Negatives). F1-Score is the harmonic mean of precision and recall, balancing both metrics.",
                "difficulty": "Beginner"
            },
            {
                "question": "How do you handle missing values in a dataset?",
                "expected_answer": "Missing values can be handled by dropping rows/columns (if minimal), imputing with mean/median/mode, or using model-based imputation algorithms like K-Nearest Neighbors (KNN) or MICE.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain the Receiver Operating Characteristic (ROC) curve and Area Under Curve (AUC).",
                "expected_answer": "The ROC curve plots True Positive Rate against False Positive Rate across various classification thresholds. AUC measures the entire 2D area under the ROC curve, representing the model's ability to distinguish between positive and negative classes (1.0 is perfect, 0.5 is random chance).",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is Feature Engineering and why is One-Hot Encoding used?",
                "expected_answer": "Feature engineering transforms raw data into numerical features that better represent business logic to ML models. One-Hot Encoding converts categorical variables into binary vectors so algorithms do not assume ordinal relationships.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain XGBoost and how gradient boosting algorithm improves upon decision trees.",
                "expected_answer": "Gradient boosting sequentially builds decision trees where each new tree fits the residual errors of the prior ensemble. XGBoost adds regularized objective functions, parallel column block structures, fast tree pruning, and built-in handling of missing values.",
                "difficulty": "Advanced"
            }
        ]
    },
    "Data Structures": {
        "Beginner": [
            {
                "question": "What is the difference between an Array and a Linked List in memory?",
                "expected_answer": "Arrays store elements in contiguous memory locations providing O(1) random index access but fixed sizing. Linked lists store nodes with pointers anywhere in memory, offering O(1) dynamic insertion/deletion but O(n) sequential access.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Stack vs Queue and what are their primary operations?",
                "expected_answer": "A Stack follows Last-In-First-Out (LIFO) with push() and pop() operations. A Queue follows First-In-First-Out (FIFO) with enqueue() and dequeue() operations.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Binary Search Tree (BST) and what is its search time complexity?",
                "expected_answer": "A BST is a node-based binary tree where left child nodes are smaller than parent node, and right child nodes are larger. Average search complexity is O(log n), degrading to O(n) if unbalanced.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Big-O Notation and why do developers analyze worst-case time complexity?",
                "expected_answer": "Big-O notation describes the upper bound limit of an algorithm's execution time or space requirement as input size n approaches infinity, ensuring scalable code selection.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is a Hash Map and how does collision resolution work?",
                "expected_answer": "A Hash Map uses a hash function to map keys to bucket array indices for O(1) key lookup. Collisions (different keys hashing to same index) are resolved using Chaining (linked lists in buckets) or Open Addressing (linear/quadratic probing).",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "Explain QuickSort vs MergeSort algorithm stability and memory complexity.",
                "expected_answer": "MergeSort is a stable divide-and-conquer algorithm with O(n log n) guaranteed time and O(n) auxiliary space complexity. QuickSort is an unstable in-place algorithm with average O(n log n) time, O(log n) stack space, but O(n^2) worst case.",
                "difficulty": "Intermediate"
            },
            {
                "question": "What is a Heap (Priority Queue) and how does Heapify work?",
                "expected_answer": "A Heap is a complete binary tree satisfying the Heap property (Min-Heap: parent <= children; Max-Heap: parent >= children). Heapify restructures an array into a valid heap in O(n) time, enabling O(log n) insertions and extractions.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain Red-Black Tree self-balancing rules and why it guarantees O(log n) height.",
                "expected_answer": "Red-Black trees are self-balancing BSTs where nodes are colored red or black. Rules dictate root and leaves (NIL) are black, red nodes cannot have red children, and every path from node to descendant leaves has equal black height. This guarantees tree height is bounded by 2 * log(n + 1).",
                "difficulty": "Advanced"
            }
        ]
    },
    "Database": {
        "Beginner": [
            {
                "question": "What is the difference between SQL (Relational) and NoSQL (Non-Relational) databases?",
                "expected_answer": "SQL databases (e.g. PostgreSQL, MySQL) are structured, table-based, use fixed schemas, and support ACID transactions. NoSQL databases (e.g. MongoDB, Redis) are document/key-value based, schema-less, and scale horizontally.",
                "difficulty": "Beginner"
            },
            {
                "question": "What are ACID properties in database transactions?",
                "expected_answer": "ACID stands for Atomicity (all operations succeed or roll back), Consistency (data satisfies integrity constraints), Isolation (concurrent transactions do not interfere), and Durability (committed changes persist after system failure).",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Database Indexing and how does it improve query speed?",
                "expected_answer": "Database indexing creates data structures (typically B-Trees or Hash Indexes) on table columns to quickly pinpoint matching rows without scanning the entire table sequentially.",
                "difficulty": "Beginner"
            },
            {
                "question": "What is Normalization and what is 3rd Normal Form (3NF)?",
                "expected_answer": "Normalization organizes database columns and tables to minimize data redundancy. 3NF requires tables to be in 2NF and ensure all non-key columns depend solely on the primary key, eliminating transitive dependencies.",
                "difficulty": "Beginner"
            },
            {
                "question": "Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN.",
                "expected_answer": "INNER JOIN returns matching rows present in both tables. LEFT JOIN returns all rows from the left table and matched rows from right table (with NULLs for unmatched). RIGHT JOIN returns all rows from the right table.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "What is Database Sharding and Horizontal Partitioning?",
                "expected_answer": "Database Sharding splits large tables horizontally across multiple server instances using a shard key, distributing computational load and storage capacity across clusters.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "Explain Multi-Version Concurrency Control (MVCC) in PostgreSQL.",
                "expected_answer": "MVCC provides concurrent database access by giving each transaction a snapshot of data at a point in time. Writes create new versions of rows instead of locking reads, preventing read-write contention.",
                "difficulty": "Advanced"
            }
        ]
    },
    "HR": {
        "Beginner": [
            {
                "question": "Tell me about yourself and your professional background.",
                "expected_answer": "A concise professional introduction covering academic background, core technical skills, key projects completed, and career aspirations relevant to the target role.",
                "difficulty": "Beginner"
            },
            {
                "question": "What are your greatest professional strengths and one area you are actively working to improve?",
                "expected_answer": "Highlight genuine technical/soft strengths (problem-solving, fast learning) with examples, and mention a real area for growth accompanied by concrete self-improvement actions.",
                "difficulty": "Beginner"
            },
            {
                "question": "Why do you want to join our organization and work in this domain?",
                "expected_answer": "Demonstrate knowledge of company domain/projects, alignment with work culture, and how this position fits long-term career development goals.",
                "difficulty": "Beginner"
            },
            {
                "question": "Describe a time when you faced a difficult challenge or conflict in a team project and how you resolved it.",
                "expected_answer": "Use the STAR method (Situation, Task, Action, Result) to detail constructive communication, active listening, problem analysis, and positive resolution.",
                "difficulty": "Beginner"
            },
            {
                "question": "Where do you see yourself in 3 to 5 years?",
                "expected_answer": "Focus on skill mastery, taking on leadership or technical architectural ownership, contributing significantly to impact metrics, and continuous growth.",
                "difficulty": "Beginner"
            }
        ],
        "Intermediate": [
            {
                "question": "How do you handle tight project deadlines or sudden changes in project scope?",
                "expected_answer": "Explain prioritization frameworks (e.g. MoSCoW), clear stakeholder communication, breaking tasks down, and managing workload without compromising code quality.",
                "difficulty": "Intermediate"
            }
        ],
        "Advanced": [
            {
                "question": "How do you handle constructive criticism or disagreement with a senior technical decision?",
                "expected_answer": "Discuss respectful dialogue based on data and technical pros/cons, seeking to understand business context, and committing fully to team alignment once a consensus or leadership decision is made.",
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
    Generates dynamic interview questions using Gemini API if key is set,
    or returns structured questions from the offline question bank in Demo Mode.
    """
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            skills_str = ", ".join(resume_skills) if resume_skills else "General core fundamentals"

            prompt = f"""
            You are an expert technical interviewer for {domain}.
            Generate exactly {num_questions} interview questions at '{difficulty}' difficulty.
            Target skills: {skills_str}.

            Format your response strictly as valid JSON with no markdown wrapping or extra text outside the JSON:
            {{
                "questions": [
                    {{
                        "question": "Question text here",
                        "expected_answer": "Detailed comprehensive expected answer here",
                        "difficulty": "{difficulty}"
                    }}
                ]
            }}
            """

            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            # Clean possible markdown block markers ```json ... ```
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
            clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            if "questions" in parsed and isinstance(parsed["questions"], list) and len(parsed["questions"]) > 0:
                return parsed["questions"][:num_questions]
        except Exception as e:
            print(f"Gemini API Question Generation failed: {e}. Falling back to Demo Mode question generator.")

    # Demo Mode / Fallback Generator
    domain_questions = OFFLINE_QUESTION_BANK.get(domain, OFFLINE_QUESTION_BANK["Software Development"])
    diff_questions = domain_questions.get(difficulty, domain_questions.get("Beginner", []))

    # If domain doesn't have enough questions for difficulty, combine all difficulties in that domain
    if len(diff_questions) < num_questions:
        all_in_domain = []
        for diff_level in ["Beginner", "Intermediate", "Advanced"]:
            all_in_domain.extend(domain_questions.get(diff_level, []))
        diff_questions = all_in_domain

    # If resume skills exist, prioritize questions touching those skills
    selected = random.sample(diff_questions, min(num_questions, len(diff_questions)))
    
    # Duplicate or expand with dynamically formatted questions if requested count exceeds fixed bank
    while len(selected) < num_questions:
        base = random.choice(diff_questions)
        skill_suffix = f" in relation to {random.choice(resume_skills)}" if resume_skills else ""
        selected.append({
            "question": f"{base['question'][:-1]}{skill_suffix}?",
            "expected_answer": base["expected_answer"],
            "difficulty": difficulty
        })

    return selected[:num_questions]
