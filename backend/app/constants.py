from app.utils.semantic_route import SemanticRoute
from app.enums import LLMType, LLMName


SEMANTIC_ROUTES = [
    SemanticRoute(
        name="greeting",
        llm_type=LLMType.WEAK,
        utterances=[
            "Hi",
            "Hello",
            "Hey",
            "Hola",
            "Bonjour",
            "Konnichiwa",
            "Salam",
            "Ciao",
        ],
    ),

    SemanticRoute(
        name="ask_to_ask",
        llm_type=LLMType.WEAK,
        utterances=[
            "can you help me?",
            "i need help.",
            "please help.",
            "can you assist me?",
            "i have a question.",
            "may I ask a question?",
            "can you answer my question?",
            "can I ask for help?",
            "will you be able to assist me?",
            "is it okay if I ask something?",
            "can you respond to my queries?",
            "tum merey sab sawalaat ke jawaab de sakte ho?",
            "meri madad kar sakte ho?",
            "kya tum madad karoge?",
            "kya tum meri madad kar sakte ho?",
            "main tumse kuch pooch sakta hoon?",
            "kya main aap se sawal kar sakta hoon?",
            "aap meri request sunoge?",
        ],
    )
    # SemanticRoute(
    #     name="urdu",
    #     llm_type=LLMType.STRONG,
    #     utterances=[
    #         "Mujhe HR policies ki details explain karo",
    #         "Kya programming seekhna asaan hai?",
    #         "میں نے اس کی تلاش کی",
    #         "میں نے اس کو دیکھا",
    #         "میں نے اسے دیکھا",
    #         "ہوا میں تازگی کا احساس بہت خوشگوار تھا۔",
    #         "کل شام ہم نے دوستوں کے ساتھ ایک خوبصورت کیفے میں کھانا کھایا۔",
    #         "کتابوں کا مطالعہ انسان کی عقل و فہم کو بڑھاتا ہے۔",
    #         "بچوں کو خوبصورت خوابوں کی تعلیم دینا ضروری ہے۔",
    #         "پہاڑی علاقے میں رہنے والے لوگ عموماً بہت مہمان نواز ہوتے ہیں۔",
    #     ]
    # ),
    # SemanticRoute(
    #     name="arabic",
    #     llm_type=LLMType.STRONG,
    #     utterances=[
    #         "ما هي سياسة الموارد البشرية لديكم؟",
    #         "هل تعتقد أن تعلم البرمجة سهل؟",
    #         "أنا أبحث عنه",
    #         "رأيته",
    #         "رأيتها",
    #         "كانت الطقس جميلة بالأمس",
    #         "أمس في المساء، تناولنا العشاء في مقهى جميل مع الأصدقاء",
    #         "قراءة الكتب تعزز العقل والفهم لدى الإنسان",
    #         "تعليم الأطفال الأحلام الجميلة ضروري",
    #         "الناس الذين يعيشون في المناطق الجبلية عادة ما يكونون مضيافين جدا",
    #         'Qira’at al-kutub tu’azziz min dhaka’ al-insan wa fahmuhu',
    #         'Hal min al-sahl ta’allum al-barmajah?',
    #         'Ashkhas al-manatiq al-jabaliyya ‘aadatan ma yakunun dayafina jiddan',
    #     ]
    # ),
    # SemanticRoute(
    #     name="multi_lingual",
    #     llm_type=LLMType.STRONG,
    #     utterances=[
    #         "kiya programming seekhna easy hai?",
    #         "mujhe HR policies ki details explain karo",
    #         "Can you tell me about the 'Parlez-vous anglais?'",
    #         "¿Dónde está el 'supermercado'?",
    #         "我想知道 'weather' 的中文是什么?",
    #     ],
    # ),

]

DEFAULT_STRONG_MODEL_NAME = LLMName.GPT_4_O
DEFAULT_WEAK_MODEL_NAME = LLMName.LLAMA3_8B
