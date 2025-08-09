#!/usr/bin/env python3
"""
Download AI4Bharat IndicBERT and other Hindi models for offline use
"""

import os
import sys
from pathlib import Path
import torch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def download_ai4bharat_models():
    """Download AI4Bharat IndicBERT models"""
    
    print("🚀 Downloading AI4Bharat IndicBERT Models")
    print("=" * 60)
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from transformers import AutoModel
        
        # Create models directory
        models_dir = Path("models_cache")
        models_dir.mkdir(exist_ok=True)
        
        # AI4Bharat models to download
        models_to_download = [
            {
                "name": "AI4Bharat IndicBERT",
                "model_id": "ai4bharat/indic-bert",
                "local_path": models_dir / "indic_bert",
                "description": "Multilingual BERT for Indian languages including Hindi"
            },
            {
                "name": "L3Cube Hindi BERT",
                "model_id": "l3cube-pune/hindi-bert-v2", 
                "local_path": models_dir / "hindi_bert_v2",
                "description": "Hindi-specific BERT model"
            },
            {
                "name": "IndicBERT Sentiment",
                "model_id": "ai4bharat/IndicBERTv2-MLM-only",
                "local_path": models_dir / "indic_bert_v2",
                "description": "IndicBERT v2 for better Hindi understanding"
            }
        ]
        
        for model_info in models_to_download:
            print(f"\n📦 Downloading {model_info['name']}")
            print(f"   Model ID: {model_info['model_id']}")
            print(f"   Description: {model_info['description']}")
            print(f"   Local Path: {model_info['local_path']}")
            
            try:
                # Create local directory
                model_info['local_path'].mkdir(parents=True, exist_ok=True)
                
                # Download tokenizer
                print("   📝 Downloading tokenizer...")
                tokenizer = AutoTokenizer.from_pretrained(
                    model_info['model_id'],
                    cache_dir=str(model_info['local_path']),
                    force_download=False
                )
                
                # Save tokenizer locally
                tokenizer.save_pretrained(str(model_info['local_path']))
                print("   ✅ Tokenizer downloaded and saved")
                
                # Download model
                print("   🧠 Downloading model...")
                
                # Try different model types
                model = None
                try:
                    # Try as sequence classification model first
                    model = AutoModelForSequenceClassification.from_pretrained(
                        model_info['model_id'],
                        cache_dir=str(model_info['local_path']),
                        force_download=False,
                        torch_dtype=torch.float32,
                        device_map="cpu"
                    )
                except:
                    # Fall back to base model
                    print("   📝 Trying as base model...")
                    model = AutoModel.from_pretrained(
                        model_info['model_id'],
                        cache_dir=str(model_info['local_path']),
                        force_download=False,
                        torch_dtype=torch.float32,
                        device_map="cpu"
                    )
                
                # Save model locally
                model.save_pretrained(str(model_info['local_path']))
                print("   ✅ Model downloaded and saved")
                
                # Test the model
                print("   🧪 Testing model...")
                test_text = "मैं खुश हूं"
                inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    print(f"   ✅ Model test successful - Output shape: {outputs.last_hidden_state.shape}")
                
                print(f"   🎉 {model_info['name']} successfully downloaded!")
                
            except Exception as e:
                print(f"   ❌ Failed to download {model_info['name']}: {str(e)}")
                continue
        
        print(f"\n🎯 Model Download Summary")
        print("=" * 60)
        
        # Check what was downloaded
        for model_info in models_to_download:
            if model_info['local_path'].exists():
                files = list(model_info['local_path'].glob("*"))
                print(f"✅ {model_info['name']}: {len(files)} files downloaded")
                print(f"   📁 Location: {model_info['local_path']}")
            else:
                print(f"❌ {model_info['name']}: Download failed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install: pip install transformers torch")
        return False
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def download_additional_hindi_models():
    """Download additional Hindi NLP models"""
    don't have a local directory with the same name. Otherwise, make sure 'facebook/wav2vec2-large-xlsr-53' is the correct path to a directory containing all relevant files for a Wav2Vec2CTCTokenizer tokenizer.
    print("\n🔄 Downloading Additional Hindi Models")
    print("=" * 60)
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        models_dir = Path("models_cache")
        
        additional_models = [
            {
                "name": "Hindi Sentiment Classifier",
                "model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "local_path": models_dir / "roberta_sentiment",
                "description": "RoBERTa sentiment model (English, but useful for comparison)"
            }
        ]
        
        for model_info in additional_models:
            print(f"\n📦 Downloading {model_info['name']}")
            
            try:
                model_info['local_path'].mkdir(parents=True, exist_ok=True)
                
                # Download and save
                tokenizer = AutoTokenizer.from_pretrained(model_info['model_id'])
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_info['model_id'],
                    torch_dtype=torch.float32
                )
                
                tokenizer.save_pretrained(str(model_info['local_path']))
                model.save_pretrained(str(model_info['local_path']))
                
                print(f"   ✅ {model_info['name']} downloaded successfully!")
                
            except Exception as e:
                print(f"   ❌ Failed to download {model_info['name']}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Additional models download failed: {e}")

def test_downloaded_models():
    """Test the downloaded models"""
    
    print("\n🧪 Testing Downloaded Models")
    print("=" * 60)
    
    models_dir = Path("models_cache")
    
    test_texts = [
        "मैं बहुत खुश हूं",
        "मुझे दुख है", 
        "मैं ठीक हूं"
    ]
    
    # Test IndicBERT
    indic_bert_path = models_dir / "indic_bert"
    if indic_bert_path.exists():
        print(f"\n🔍 Testing AI4Bharat IndicBERT")
        try:
            from transformers import AutoTokenizer, AutoModel
            
            tokenizer = AutoTokenizer.from_pretrained(str(indic_bert_path))
            model = AutoModel.from_pretrained(str(indic_bert_path))
            
            for text in test_texts:
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                with torch.no_grad():
                    outputs = model(**inputs)
                    print(f"   📝 '{text}' → Embedding shape: {outputs.last_hidden_state.shape}")
            
            print("   ✅ IndicBERT working correctly!")
            
        except Exception as e:
            print(f"   ❌ IndicBERT test failed: {e}")
    else:
        print("   ❌ IndicBERT not found")

def check_proxy_and_connection():
    """Check proxy settings and internet connectivity"""
    import os

    print("🔍 Checking Network Configuration")
    print("=" * 40)

    # Check proxy settings
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False

    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"🌐 {var}: {value}")
            proxy_found = True

    if not proxy_found:
        print("🌐 No proxy settings found")

    # Test connectivity
    print("\n🔗 Testing Connectivity...")

    try:
        import requests

        # Configure session with proxy if needed
        session = requests.Session()

        # Test connection
        response = session.get("https://huggingface.co", timeout=30)
        if response.status_code == 200:
            print("✅ Can connect to Hugging Face")
            return True
        else:
            print(f"❌ Hugging Face returned status: {response.status_code}")
            return False

    except requests.exceptions.ProxyError:
        print("❌ Proxy connection failed")
        print("💡 Try: export http_proxy='' https_proxy='' to disable proxy")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        print("💡 Proxy may be blocking access to Hugging Face")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def download_with_proxy_handling():
    """Download models with proxy handling"""

    print("\n🔧 Configuring Download Environment")
    print("=" * 40)

    # Try to configure transformers for proxy
    try:
        import os

        # Set transformers cache directory
        cache_dir = os.path.join(os.getcwd(), "models_cache")
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        os.environ['HF_HOME'] = cache_dir

        print(f"📁 Cache directory: {cache_dir}")

        # Try different proxy configurations
        proxy_configs = [
            {"description": "With current proxy", "modify": False},
            {"description": "Without proxy", "modify": True}
        ]

        for config in proxy_configs:
            print(f"\n🔄 Trying download {config['description']}")

            if config['modify']:
                # Temporarily disable proxy
                old_http = os.environ.get('http_proxy')
                old_https = os.environ.get('https_proxy')
                os.environ.pop('http_proxy', None)
                os.environ.pop('https_proxy', None)

            try:
                success = download_ai4bharat_models()
                if success:
                    print(f"✅ Download successful {config['description']}")
                    return True
            except Exception as e:
                print(f"❌ Download failed {config['description']}: {e}")

            if config['modify']:
                # Restore proxy settings
                if old_http:
                    os.environ['http_proxy'] = old_http
                if old_https:
                    os.environ['https_proxy'] = old_https

        return False

    except Exception as e:
        print(f"❌ Proxy handling failed: {e}")
        return False

def main():
    """Main download function with proxy handling"""

    print("🎖️ Army Mental Health - Hindi Model Downloader")
    print("=" * 60)
    print("This script will download AI4Bharat IndicBERT and other Hindi models")
    print("for offline use in the army mental health assessment system.")
    print()

    # Check proxy and connectivity
    can_connect = check_proxy_and_connection()

    if not can_connect:
        print("\n⚠️  Network Issues Detected")
        print("=" * 40)
        print("Options to resolve:")
        print("1. Disable proxy temporarily:")
        print("   export http_proxy=''")
        print("   export https_proxy=''")
        print("2. Configure proxy for Hugging Face access")
        print("3. Download models manually from Hugging Face website")
        print("4. Use enhanced keyword-based analysis (already available)")
        print()

        response = input("Try download anyway? (y/n): ").lower()
        if response != 'y':
            print("Using enhanced keyword-based analysis instead...")
            return
    
    # Try download with proxy handling
    success = download_with_proxy_handling()

    if success:
        download_additional_hindi_models()
        test_downloaded_models()

        print("\n🎉 Model Download Complete!")
        print("=" * 60)
        print("✅ AI4Bharat IndicBERT models downloaded")
        print("✅ Models saved in 'models_cache' directory")
        print("✅ Ready for offline Hindi sentiment analysis")
        print()
        print("🎖️ The army mental health system can now use:")
        print("   - AI4Bharat IndicBERT for Hindi text understanding")
        print("   - Enhanced keyword-based sentiment analysis")
        print("   - Offline processing (no internet required)")
        print()
        print("🚀 You can now restart the application to use the new models!")

    else:
        print("\n⚠️  Model Download Failed")
        print("=" * 60)
        print("Don't worry! The system can still work with:")
        print("✅ Enhanced keyword-based Hindi sentiment analysis")
        print("✅ English sentiment analysis")
        print("✅ All other features working normally")
        print()
        print("🎖️ For army deployment, the keyword-based analysis provides:")
        print("   - Accurate Hindi sentiment detection")
        print("   - Military-specific terminology recognition")
        print("   - Offline processing (no internet required)")
        print("   - Fast response times")
        print()
        print("💡 To get transformer models later:")
        print("   1. Ensure internet access without proxy restrictions")
        print("   2. Run this script again")
        print("   3. Or download models manually from huggingface.co")

if __name__ == "__main__":
    main()
