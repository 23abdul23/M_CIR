# सेना मानसिक स्वास्थ्य मूल्यांकन प्रणाली
# Army Mental Health Assessment System

एक व्यापक मानसिक स्वास्थ्य मूल्यांकन प्रणाली जो हिंदी भाषा में सैनिकों के लिए डिज़ाइन की गई है।

## विशेषताएं (Features)

### 🎯 मुख्य विशेषताएं
- **हिंदी प्रश्नावली**: सैनिकों के लिए विशेष रूप से डिज़ाइन की गई हिंदी प्रश्नावली
- **आवाज़ से मूल्यांकन**: हिंदी में बोलकर मानसिक स्वास्थ्य का मूल्यांकन
- **AI विश्लेषण**: उन्नत AI मॉडल का उपयोग करके भावना और कीवर्ड विश्लेषण
- **व्यापक रिपोर्टिंग**: विस्तृत मानसिक स्वास्थ्य रिपोर्ट और सुझाव

### 🔧 तकनीकी विशेषताएं
- **Streamlit UI**: उपयोगकर्ता-अनुकूल वेब इंटरफेस
- **SQLite Database**: स्थानीय डेटाबेस भंडारण
- **Hindi NLP**: हिंदी भाषा प्रसंस्करण
- **Voice Processing**: आवाज़ से टेक्स्ट रूपांतरण
- **Admin Panel**: प्रश्नावली प्रबंधन के लिए एडमिन पैनल

## स्थापना (Installation)

### आवश्यकताएं
- Python 3.8 या उससे ऊपर
- pip package manager

### स्थापना चरण

1. **Repository clone करें:**
```bash
git clone <repository-url>
cd army_mental_health
```

2. **Setup script चलाएं:**
```bash
python setup.py
```

3. **Application चलाएं:**
```bash
python run.py
```

4. **Browser में खोलें:**
   - http://localhost:8501 पर जाएं

## उपयोग (Usage)

### डिफ़ॉल्ट लॉगिन
- **Admin Login:**
  - Username: `admin`
  - Password: `admin123`

### उपयोगकर्ता के लिए
1. लॉगिन करें
2. "मूल्यांकन करें" टैब में जाएं
3. प्रश्नावली चुनें और पूरा करें
4. या "आवाज़ से मूल्यांकन" का उपयोग करें

### एडमिन के लिए
1. Admin के रूप में लॉगिन करें
2. प्रश्नावली प्रबंधन
3. उपयोगकर्ता प्रबंधन
4. रिपोर्ट्स देखें

## फ़ाइल संरचना

```
army_mental_health/
├── src/
│   ├── app.py                 # मुख्य Streamlit application
│   ├── database/              # डेटाबेस मॉड्यूल
│   ├── models/                # AI मॉडल्स
│   ├── admin/                 # एडमिन इंटरफेस
│   └── config.py              # कॉन्फ़िगरेशन
├── data/                      # डेटा फ़ाइलें
├── requirements.txt           # Python dependencies
├── setup.py                   # Setup script
└── run.py                     # Run script
```

## समस्या निवारण (Troubleshooting)

### सामान्य समस्याएं

1. **Audio processing नहीं हो रहा:**
   - PyAudio install करें: `pip install pyaudio`
   - Windows पर: Microsoft Visual C++ Build Tools install करें

2. **Hindi models download नहीं हो रहे:**
   - Internet connection check करें
   - Firewall settings check करें

3. **Database errors:**
   - `python setup.py` फिर से चलाएं
   - data/ directory की permissions check करें

## योगदान (Contributing)

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## लाइसेंस (License)

यह प्रोजेक्ट MIT License के तहत है।

## संपर्क (Contact)

तकनीकी सहायता के लिए संपर्क करें।
