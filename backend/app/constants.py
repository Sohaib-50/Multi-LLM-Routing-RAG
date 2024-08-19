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
