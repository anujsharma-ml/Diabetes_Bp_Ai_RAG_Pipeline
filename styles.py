# styles.py

CUSTOM_CSS = r"""
    <style>
        /* Hide Default Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Base Canvas Background */
        .stApp {
            background-color: #060609 !important;
            color: #E4E4E7 !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            overflow-x: hidden;
        }

        /* Ambient Pulsing Glow Animations */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: 
                radial-gradient(circle at 15% 25%, rgba(239, 68, 68, 0.18) 0%, transparent 45%),
                radial-gradient(circle at 85% 75%, rgba(59, 130, 246, 0.14) 0%, transparent 45%),
                radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 55%);
            z-index: 0;
            pointer-events: none;
            animation: ambientGlow 8s ease-in-out infinite alternate;
        }

        @keyframes ambientGlow {
            0% { transform: scale(1); opacity: 0.6; }
            100% { transform: scale(1.08); opacity: 1; }
        }

        /* Moving 3D Wave Visuals at Bottom */
        .stApp::after {
            content: "";
            position: fixed;
            bottom: 0;
            left: 0;
            width: 200vw;
            height: 220px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 140' preserveAspectRatio='none'%3E%3Cpath d='M0,30 C150,110 350,-20 500,50 C650,120 950,10 1200,70 L1200,140 L0,140 Z' fill='rgba(239, 68, 68, 0.15)'/%3E%3Cpath d='M0,60 C200,10 400,130 600,60 C800,-10 1000,110 1200,40 L1200,140 L0,140 Z' fill='rgba(59, 130, 246, 0.08)'/%3E%3C/svg%3E");
            background-repeat: repeat-x;
            background-size: 50% 160px;
            animation: vesselFlow 12s linear infinite;
            z-index: 0;
            pointer-events: none;
        }

        @keyframes vesselFlow {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        /* Layering Fix to Keep UI Above Background Visuals */
        .main .block-container {
            position: relative;
            z-index: 2;
            max-width: 780px;
            padding-top: 1.2rem;
            padding-bottom: 5.5rem;
        }

        /* Top Workspace Navbar */
        .workspace-header {
            background: rgba(14, 14, 20, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 10px 18px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            width: 100%;
            box-sizing: border-box;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-icon {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.9) 0%, rgba(37, 99, 235, 0.8) 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.3);
        }

        .brand-text h2 {
            font-size: 0.92rem;
            font-weight: 700;
            color: #FAFAFA;
            margin: 0;
            letter-spacing: -0.2px;
        }

        .brand-text p {
            font-size: 0.68rem;
            color: #A1A1AA;
            margin: 0;
        }

        /* LIVE Pulse Badge */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(220, 38, 38, 0.12);
            border: 1px solid rgba(220, 38, 38, 0.3);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.70rem;
            color: #F87171;
            font-weight: 600;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            background-color: #EF4444;
            border-radius: 50%;
            box-shadow: 0 0 8px #EF4444;
            animation: softPulse 1.8s infinite;
        }

        @keyframes softPulse {
            0% { opacity: 0.4; transform: scale(0.9); }
            50% { opacity: 1; transform: scale(1.3); }
            100% { opacity: 0.4; transform: scale(0.9); }
        }

        /* Glassmorphism Welcome Hero Card */
        .dashboard-welcome {
            background: linear-gradient(145deg, rgba(18, 18, 26, 0.75) 0%, rgba(10, 10, 16, 0.9) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
            margin-bottom: 20px;
        }

        .dashboard-welcome h1 {
            font-size: 1.25rem;
            font-weight: 700;
            color: #FAFAFA;
            margin-bottom: 8px;
        }

        .dashboard-welcome p {
            font-size: 0.84rem;
            color: #9CA3AF;
            max-width: 480px;
            margin: 0 auto;
            line-height: 1.5;
        }

        /* Buttons */
        div.stButton > button {
            width: 100% !important;
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: rgba(18, 18, 26, 0.85) !important;
            color: #D4D4D8 !important;
            padding: 9px 16px !important;
            font-size: 0.82rem !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        div.stButton > button:hover {
            border-color: rgba(220, 38, 38, 0.45) !important;
            background: rgba(220, 38, 38, 0.12) !important;
            color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.2);
        }

        /* Chat Message Bubbles */
        .stChatMessage[data-testid="stChatMessage-user"] {
            background: linear-gradient(135deg, #B91C1C 0%, #881337 100%) !important;
            border-radius: 20px 20px 4px 20px !important;
            padding: 12px 18px !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 16px rgba(185, 28, 28, 0.25);
            max-width: 80%;
            margin-left: auto !important;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        .stChatMessage[data-testid="stChatMessage-user"] p,
        .stChatMessage[data-testid="stChatMessage-user"] span {
            color: #FFFFFF !important;
            font-size: 0.89rem !important;
            line-height: 1.55 !important;
        }

        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background: rgba(14, 14, 20, 0.82) !important;
            backdrop-filter: blur(16px);
            border-radius: 20px 20px 20px 4px !important;
            padding: 16px 20px !important;
            color: #E4E4E7 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45) !important;
            max-width: 88%;
            margin-right: auto !important;
        }
        
        .stChatMessage[data-testid="stChatMessage-assistant"] p,
        .stChatMessage[data-testid="stChatMessage-assistant"] li,
        .stChatMessage[data-testid="stChatMessage-assistant"] span {
            color: #E4E4E7 !important;
            font-size: 0.89rem !important;
            line-height: 1.6 !important;
        }

        /* Curved Input Box */
        div[data-testid="stChatInputContainer"] {
            background: rgba(6, 6, 9, 0.85) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 12px 0 20px 0 !important;
            width: 100% !important;
            max-width: 780px !important;
            margin: 0 auto !important;
        }

        div[data-testid="stChatInput"] {
            background-color: rgba(16, 16, 24, 0.85) !important;
            border-radius: 32px !important;
            border: 1px solid rgba(255, 255, 255, 0.10) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
            padding: 6px 14px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stChatInput"]:focus-within {
            border-color: rgba(220, 38, 38, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15), 0 8px 30px rgba(0, 0, 0, 0.7) !important;
            background-color: rgba(20, 20, 30, 0.95) !important;
        }

        div[data-testid="stChatInput"] textarea {
            color: #F4F4F5 !important;
            font-size: 0.90rem !important;
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #71717A !important;
        }

        div[data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
            border: none !important;
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stChatInput"] button:hover {
            opacity: 0.95 !important;
            transform: scale(1.06);
            box-shadow: 0 0 10px rgba(220, 38, 38, 0.4);
        }

        /* Footer */
        .app-footer {
            text-align: center;
            padding: 16px 10px;
            font-size: 0.72rem;
            color: #6B7280;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 24px;
            line-height: 1.5;
        }
    </style>
"""

NAVBAR_HTML = """
    <div class="workspace-header">
        <div class="header-brand">
            <div class="brand-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.5 13.5C19.5 17.6421 16.1421 21 12 21C7.85786 21 4.5 17.6421 4.5 13.5C4.5 9.35786 7.85786 6 12 6" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <path d="M12 2V6" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <path d="M9 13.5H11L12.5 10.5L14 16.5L15.5 13.5H17.5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="2" r="1.5" fill="white"/>
                </svg>
            </div>
            <div class="brand-text">
                <h2>MediPulse AI</h2>
                <p>Clinical Intelligence Assistant</p>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>LIVE</span>
        </div>
    </div>
"""

WELCOME_HERO_HTML = """
    <div class="dashboard-welcome">
        <h1>Clinical Intelligence at Your Fingertips</h1>
        <p>Query evidence-based medical protocols, diagnostic threshold ranges, and clinical guidelines instantly.</p>
    </div>
"""

FOOTER_HTML = """
    <div class="app-footer">
        <p>⚠️ <b>MediPulse AI</b> provides clinical decision support and is not a substitute for professional medical diagnosis.<br>
        © 2026 MediPulse AI. All rights reserved.</p>
    </div>
"""