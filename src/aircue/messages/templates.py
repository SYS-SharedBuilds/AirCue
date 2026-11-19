"""Pre-defined announcement templates for English and Hindi (Devanagari).

All templates strictly adhere to outdoor activity guidance:
- Under 20 words where possible.
- Polite, clear, direct outdoor action instructions.
- Absolutely NO indoor, ventilation, door, or window references.
"""
from __future__ import annotations

from typing import NamedTuple


class TemplateSet(NamedTuple):
    neutral: str
    young: str
    assembly: str
    sports_pt: str
    recess: str
    dismissal: str


# English Announcement Templates
TEMPLATES_EN: dict[str, TemplateSet] = {
    # Escalate Levels 1-4
    "escalate_1": TemplateSet(
        neutral="Air quality is moderate. Sensitive students please avoid heavy outdoor exertion.",
        young="The air is a bit dusty today. Sensitive friends please take it easy outside.",
        assembly="Air quality is moderate. Please keep morning assembly brief and light.",
        sports_pt="Air quality is moderate. Sensitive students please take frequent rests during sports.",
        recess="Air quality is moderate. Please prefer gentle games during recess.",
        dismissal="Air quality is moderate. Please proceed calmly to your school buses.",
    ),
    "escalate_2": TemplateSet(
        neutral="Air quality is poor. Please reduce outdoor activities and play indoors.",
        young="Air quality is poor. Let us head indoors for today's games.",
        assembly="Air quality is poor. Please move the remaining assembly indoors.",
        sports_pt="Air quality is poor. Please conduct physical training indoors.",
        recess="Air quality is poor. Please enjoy indoor games during recess today.",
        dismissal="Air quality is poor. Please board school buses promptly without lingering outdoors.",
    ),
    "escalate_3": TemplateSet(
        neutral="Air quality is very poor. Please move all outdoor activities indoors.",
        young="The outdoor air is very dusty. Everyone please stay inside classrooms.",
        assembly="Air quality is very poor. Morning assembly is moved indoors immediately.",
        sports_pt="Air quality is very poor. All outdoor sports are shifted indoors.",
        recess="Air quality is very poor. Recess will be held indoors today.",
        dismissal="Air quality is very poor. Please walk directly to school transport.",
    ),
    "escalate_4": TemplateSet(
        neutral="Air quality is severe. Please keep everyone indoors and cancel outdoor activities.",
        young="The air outside is unhealthy today. Everyone must remain indoors.",
        assembly="Air quality is severe. Outdoor assembly is cancelled; remain inside.",
        sports_pt="Air quality is severe. All outdoor sports sessions are cancelled.",
        recess="Air quality is severe. All students must remain indoors during break.",
        dismissal="Air quality is severe. Move straight from classrooms to school buses.",
    ),
    # Reminders Levels 1-4
    "reminder_1": TemplateSet(
        neutral="Reminder: air quality remains moderate. Sensitive students please limit heavy exertion.",
        young="Gentle reminder: please remember to take rests if you feel tired outside.",
        assembly="Reminder: keep outdoor gathering brief due to moderate air quality.",
        sports_pt="Reminder: ensure sensitive students rest during outdoor training.",
        recess="Reminder: take gentle rests during outdoor play.",
        dismissal="Reminder: air is moderate; proceed directly to your transport.",
    ),
    "reminder_2": TemplateSet(
        neutral="Reminder: air quality is poor. Please keep outdoor activities reduced.",
        young="Friendly reminder: please continue playing indoors today.",
        assembly="Reminder: please conduct student gatherings indoors.",
        sports_pt="Reminder: keep physical training indoors while air remains poor.",
        recess="Reminder: please stay indoors for recess activities.",
        dismissal="Reminder: air quality is poor; board your buses promptly.",
    ),
    "reminder_3": TemplateSet(
        neutral="Reminder: air quality remains very poor. All activities must stay indoors.",
        young="Reminder: please stay inside where the air is safe.",
        assembly="Reminder: outdoor gatherings remain suspended.",
        sports_pt="Reminder: outdoor sports remain suspended indoors.",
        recess="Reminder: outdoor recess remains suspended today.",
        dismissal="Reminder: air is very poor; move swiftly to school transport.",
    ),
    "reminder_4": TemplateSet(
        neutral="Urgent reminder: air quality is severe. Strictly avoid outdoor exposure.",
        young="Important reminder: please do not go outdoors today.",
        assembly="Urgent reminder: outdoor assembly strictly prohibited.",
        sports_pt="Urgent reminder: all outdoor sports strictly cancelled.",
        recess="Urgent reminder: stay indoors; outdoor break strictly cancelled.",
        dismissal="Urgent reminder: proceed immediately to school buses.",
    ),
    # Improving & Recovered
    "improving": TemplateSet(
        neutral="Air quality is improving, but please keep outdoor physical activity light.",
        young="The air is getting clearer, but let us still play gently outside.",
        assembly="Air quality is improving. Assembly may proceed with light activities.",
        sports_pt="Air quality is improving. Light outdoor training may resume with care.",
        recess="Air quality is improving. Gentle outdoor play is permitted.",
        dismissal="Air quality is improving. Have a safe journey home.",
    ),
    "recovered": TemplateSet(
        neutral="Thank you. Air quality is good again. Outdoor activities can resume.",
        young="Great news! The air is clean and fresh again. Enjoy your outdoor play!",
        assembly="Air quality has returned to normal. Outdoor assembly may proceed.",
        sports_pt="Air quality is good. Regular outdoor sports and games may resume.",
        recess="Air quality is good. Normal outdoor playground recess can resume.",
        dismissal="Air quality is good. Have a wonderful and safe evening.",
    ),
}

# Hindi Announcement Templates (Devanagari)
TEMPLATES_HI: dict[str, TemplateSet] = {
    "escalate_1": TemplateSet(
        neutral="वायु गुणवत्ता मध्यम है। संवेदनशील छात्र कृपया बाहर अधिक श्रम न करें।",
        young="बाहर थोड़ी धूल है। संवेदनशील बच्चे कृपया बाहर आराम से खेलें।",
        assembly="वायु गुणवत्ता मध्यम है। कृपया सुबह की सभा संक्षिप्त रखें।",
        sports_pt="वायु गुणवत्ता मध्यम है। खेलकूद के दौरान छात्र बीच-बीच में विश्राम लें।",
        recess="वायु गुणवत्ता मध्यम है। भोजन अवकाश में हल्के खेल ही खेलें।",
        dismissal="वायु गुणवत्ता मध्यम है। कृपया शांतिपूर्वक अपनी बसों की ओर बढ़ें।",
    ),
    "escalate_2": TemplateSet(
        neutral="वायु गुणवत्ता खराब है। कृपया बाहरी गतिविधियाँ कम करें और भीतर खेलें।",
        young="बाहर हवा खराब है। आइए आज भीतर ही खेलें।",
        assembly="वायु गुणवत्ता खराब है। कृपया सभा भीतर आयोजित करें।",
        sports_pt="वायु गुणवत्ता खराब है। शारीरिक व्यायाम भीतर ही कराएं।",
        recess="वायु गुणवत्ता खराब है। अवकाश के समय भीतर ही रहें।",
        dismissal="वायु गुणवत्ता खराब है। छात्र तुरंत अपने वाहनों में बैठें।",
    ),
    "escalate_3": TemplateSet(
        neutral="वायु गुणवत्ता बहुत खराब है। कृपया सभी बाहरी गतिविधियाँ तुरंत भीतर ले जाएं।",
        young="बाहर बहुत धूल और प्रदूषण है। सभी बच्चे कक्षाओं के भीतर रहें।",
        assembly="वायु गुणवत्ता बहुत खराब है। सुबह की सभा तुरंत भीतर स्थानांतरित करें।",
        sports_pt="वायु गुणवत्ता बहुत खराब है। बाहरी खेलकूद पूरी तरह बंद रखें।",
        recess="वायु गुणवत्ता बहुत खराब है। अवकाश के दौरान सभी छात्र भीतर ही रहें।",
        dismissal="वायु गुणवत्ता बहुत खराब है। छात्र सीधे स्कूल बस की ओर जाएं।",
    ),
    "escalate_4": TemplateSet(
        neutral="वायु गुणवत्ता गंभीर है। कृपया सभी को भीतर रखें और बाहरी कार्यक्रम रद्द करें।",
        young="बाहर हवा बहुत अस्वास्थ्यकर है। किसी को बाहर जाने की अनुमति नहीं है।",
        assembly="वायु गुणवत्ता गंभीर है। बाहरी सभा तुरंत रद्द की जाती है।",
        sports_pt="वायु गुणवत्ता गंभीर है। सभी बाहरी खेल प्रतियोगिताएं रद्द हैं।",
        recess="वायु गुणवत्ता गंभीर है। कोई भी छात्र बाहर मैदान में न जाए।",
        dismissal="वायु गुणवत्ता गंभीर है। बिना रुके सीधे स्कूल बस में बैठें।",
    ),
    "reminder_1": TemplateSet(
        neutral="स्मरण: वायु गुणवत्ता मध्यम है। संवेदनशील छात्र अधिक श्रम से बचें।",
        young="याद रखें: यदि बाहर थकान लगे तो विश्राम अवश्य करें।",
        assembly="स्मरण: वायु गुणवत्ता को देखते हुए सभा को संक्षिप्त रखें।",
        sports_pt="स्मरण: खेलकूद में छात्रों को पर्याप्त विश्राम दें।",
        recess="स्मरण: खेल के दौरान अधिक दौड़-भाग से बचें।",
        dismissal="स्मरण: वायु गुणवत्ता मध्यम है, सीधे वाहन की ओर जाएं।",
    ),
    "reminder_2": TemplateSet(
        neutral="स्मरण: वायु गुणवत्ता खराब है। कृपया बाहरी गतिविधियाँ सीमित रखें।",
        young="याद दिलाना है: कृपया आज बाहर न खेलें, भीतर ही रहें।",
        assembly="स्मरण: सभी छात्र सभाएं भीतर ही आयोजित की जाएं।",
        sports_pt="स्मरण: व्यायाम और पीटी केवल कमरों के भीतर करें।",
        recess="स्मरण: अवकाश के दौरान मैदान में न जाएं।",
        dismissal="स्मरण: वायु खराब है, तुरंत अपने वाहनों में सवार हों।",
    ),
    "reminder_3": TemplateSet(
        neutral="स्मरण: वायु गुणवत्ता बहुत खराब बनी हुई है। सभी गतिविधियाँ भीतर ही रखें।",
        young="याद रखें: बाहर जाना मना है, सब भीतर सुरक्षित रहें।",
        assembly="स्मरण: बाहरी सभा पूरी तरह स्थगित है।",
        sports_pt="स्मरण: बाहरी खेल पूरी तरह स्थगित हैं।",
        recess="स्मरण: कोई भी बच्चा मैदान में न जाए।",
        dismissal="स्मरण: प्रदूषण अधिक है, तेजी से बसों में बैठें।",
    ),
    "reminder_4": TemplateSet(
        neutral="अति आवश्यक स्मरण: वायु गुणवत्ता गंभीर है। बाहरी संपर्क से पूरी तरह बचें।",
        young="महत्वपूर्ण सूचना: किसी भी कारण से बाहर मैदान में न निकलें।",
        assembly="अति आवश्यक: बाहर एकत्रित होना सख्त मना है।",
        sports_pt="अति आवश्यक: सभी खेल गतिविधियाँ पूर्णतः रद्द हैं।",
        recess="अति आवश्यक: सभी छात्र कक्षाओं के भीतर ही रहें।",
        dismissal="अति आवश्यक: सीधे कक्षा से निकलकर बसों में बैठें।",
    ),
    "improving": TemplateSet(
        neutral="वायु गुणवत्ता में सुधार हो रहा है, फिर भी बाहरी गतिविधियाँ हल्की रखें।",
        young="हवा साफ हो रही है, पर अभी भी आराम से ही खेलना है।",
        assembly="वायु गुणवत्ता सुधर रही है। संक्षिप्त सभा की जा सकती है।",
        sports_pt="वायु गुणवत्ता सुधर रही है। हल्का अभ्यास शुरू कर सकते हैं।",
        recess="वायु गुणवत्ता में सुधार है। हल्का खेलकूद कर सकते हैं।",
        dismissal="वायु गुणवत्ता सुधर रही है। आपकी यात्रा मंगलमय हो।",
    ),
    "recovered": TemplateSet(
        neutral="धन्यवाद। वायु गुणवत्ता पुनः अच्छी हो गई है। बाहरी गतिविधियाँ शुरू हो सकती हैं।",
        young="खुशखबरी! हवा फिर से ताज़ा और साफ है। अब आप बाहर खेल सकते हैं!",
        assembly="वायु गुणवत्ता सामान्य है। बाहरी सभा पुनः शुरू की जा सकती है।",
        sports_pt="वायु गुणवत्ता अच्छी है। खेल के मैदान में अभ्यास शुरू कर सकते हैं।",
        recess="वायु गुणवत्ता अच्छी है। मैदान में खेलना फिर से शुरू हो सकता है।",
        dismissal="वायु गुणवत्ता अच्छी है। सभी छात्र सुरक्षित घर लौटें।",
    ),
}
