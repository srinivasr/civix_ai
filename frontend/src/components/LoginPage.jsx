import React, { useState } from 'react';
import {
    ShieldCheck, User, Lock, Building2, MapPin,
    ArrowRight, Globe, BadgeCheck
} from 'lucide-react';
import logo from '../assets/logo.png';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
    const [view, setView] = useState('login'); // 'signup' or 'login'
    const [userType, setUserType] = useState('booth'); // 'booth' or 'official'

    const navy = "#0f172a";
    const gold = "#D4AF37";
    const slate400 = "#94a3b8";
    const slate500 = "#64748b";
    const slate50 = "#f8fafc";
    const slate100 = "#f1f5f9";
    const slate200 = "#e2e8f0";
    const white = "#ffffff";

    const [boothIdInput, setBoothIdInput] = useState('');
    const [nameInput, setNameInput] = useState('');
    const [passwordInput, setPasswordInput] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, signup } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const email = userType === 'booth'
            ? `booth_${boothIdInput}@innovateindia.gov`
            : `official_${nameInput}@innovateindia.gov`;

        try {
            if (view === 'login') {
                await login(email, passwordInput);
            } else {
                const metadata = userType === 'booth'
                    ? { name: nameInput }
                    : { department: 'System Default' };
                await signup(email, passwordInput, userType, metadata);
            }
        } catch (err) {
            console.error(err);
            if (err.code === 'invalid-credentials') {
                setError('Account not found or invalid credentials. Please register your access first.');
            } else if (err.code === 'email-already-in-use') {
                setError('This ID is already registered. Please sign in instead.');
            } else {
                setError(err.message || 'Authentication failed. Please verify your details.');
            }
        }
        setLoading(false);
    };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100%', backgroundColor: white, fontFamily: 'Public Sans, sans-serif', overflow: 'hidden' }}>

            {/* LEFT SIDE: Solid Navy Branding */}
            <div style={{
                display: 'none', // Default hidden for mobile
                width: '50%',
                backgroundColor: navy,
                flexDirection: 'column',
                justifyContent: 'center',
                padding: '0 80px',
                position: 'relative'
            }} className="lg-flex">
                <style dangerouslySetInnerHTML={{
                    __html: `
          @media (min-width: 1024px) {
            .lg-flex { display: flex !important; }
          }
        `}} />
                <div style={{ maxWidth: '448px', position: 'relative', zIndex: 10 }}>
                    <div style={{ display: 'flex', flexDirection: 'column', marginBottom: '64px' }}>
                        <img src={logo} alt="Logo" style={{ height: '120px', objectFit: 'contain', objectPosition: 'left', display: 'block', marginBottom: '32px' }} />
                        <div style={{ height: '6px', width: '80px', backgroundColor: gold, marginBottom: '24px' }} />
                        <span style={{ color: slate500, fontSize: '12px', fontWeight: 900, letterSpacing: '0.4em', textTransform: 'uppercase', width: 'fit-content' }}>
                            Booth Intelligence
                        </span>
                    </div>

                    <p style={{ color: slate400, fontSize: '18px', fontWeight: 500, lineHeight: 1.625, maxWidth: '384px' }}>
                        Dedicated infrastructure for Booth Officials and Government Administration.
                        Real-time complaint logging and encrypted data relay.
                    </p>
                </div>
            </div>

            {/* RIGHT SIDE: Form Portal */}
            <div style={{
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                padding: '0 32px',
                backgroundColor: white,
                overflowY: 'auto'
            }} className="right-panel">
                <style dangerouslySetInnerHTML={{
                    __html: `
          @media (min-width: 640px) { .right-panel { padding: 0 64px !important; } }
          @media (min-width: 1024px) { 
            .right-panel { width: 50% !important; padding: 0 96px !important; } 
          }
        `}} />
                <div style={{ maxWidth: '448px', width: '100%', margin: '0 auto', padding: '48px 0' }}>

                    <div style={{ marginBottom: '48px', textAlign: 'right' }}>
                        <button
                            onClick={() => setView(view === 'login' ? 'signup' : 'login')}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: slate400,
                                fontSize: '10px',
                                fontWeight: 900,
                                textTransform: 'uppercase',
                                letterSpacing: '0.1em',
                                cursor: 'pointer',
                                transition: 'color 0.15s ease'
                            }}
                            onMouseEnter={(e) => e.target.style.color = navy}
                            onMouseLeave={(e) => e.target.style.color = slate400}
                        >
                            {view === 'login' ? 'Register New Access →' : 'Already Authorized? Sign In →'}
                        </button>
                    </div>

                    <div style={{ marginBottom: '40px' }}>
                        <h2 style={{ fontSize: '30px', fontWeight: 900, color: navy, letterSpacing: '-0.025em', textTransform: 'uppercase' }}>
                            {view === 'login' ? 'Portal Login' : 'System Registration'}
                        </h2>
                        <p style={{ color: slate400, fontSize: '10px', fontWeight: 900, marginTop: '8px', textTransform: 'uppercase', letterSpacing: '0.2em' }}>
                            Authorized Access Only
                        </p>
                    </div>

                    <div style={{ display: 'flex', border: `2px solid ${slate100}`, borderRadius: '16px', marginBottom: '40px', padding: '6px', backgroundColor: slate50 }}>
                        <button
                            onClick={() => setUserType('booth')}
                            style={{
                                flex: 1,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px',
                                padding: '14px 0',
                                borderRadius: '12px',
                                fontSize: '10px',
                                fontWeight: 900,
                                letterSpacing: '0.1em',
                                border: 'none',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                backgroundColor: userType === 'booth' ? navy : 'transparent',
                                color: userType === 'booth' ? white : slate400,
                                boxShadow: userType === 'booth' ? '0 20px 25px -5px rgba(0, 0, 0, 0.1)' : 'none'
                            }}
                        >
                            <MapPin size={14} color={userType === 'booth' ? gold : slate400} /> BOOTH
                        </button>
                        <button
                            onClick={() => setUserType('official')}
                            style={{
                                flex: 1,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px',
                                padding: '14px 0',
                                borderRadius: '12px',
                                fontSize: '10px',
                                fontWeight: 900,
                                letterSpacing: '0.1em',
                                border: 'none',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                backgroundColor: userType === 'official' ? navy : 'transparent',
                                color: userType === 'official' ? white : slate400,
                                boxShadow: userType === 'official' ? '0 20px 25px -5px rgba(0, 0, 0, 0.1)' : 'none'
                            }}
                        >
                            <ShieldCheck size={14} color={userType === 'official' ? gold : slate400} /> OFFICIAL
                        </button>
                    </div>

                    {error && (
                        <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '12px 16px', borderRadius: '12px', marginBottom: '24px', fontSize: '11px', fontWeight: 700, border: '1px solid #fca5a5' }}>
                            {error}
                        </div>
                    )}

                    <form style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} onSubmit={handleSubmit}>
                        {view === 'signup' && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                {userType === 'booth' ? (
                                    <>
                                        <FlatField label="Name of the Official" icon={<User size={16} />} placeholder="In-charge Full Name" value={nameInput} onChange={setNameInput} />
                                        <FlatField label="Booth ID" icon={<BadgeCheck size={16} />} placeholder="Enter unique Booth #" value={boothIdInput} onChange={setBoothIdInput} />
                                        <FlatField label="State" icon={<Globe size={16} />} placeholder="Enter State / Union Territory" />
                                    </>
                                ) : (
                                    <>
                                        <FlatField label="Gov Official ID" icon={<ShieldCheck size={16} />} placeholder="GOV-XXXX-XXXX" value={nameInput} onChange={setNameInput} />
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                            <label style={{ fontSize: '9px', fontWeight: 900, color: slate400, textTransform: 'uppercase', letterSpacing: '0.1em', marginLeft: '4px' }}>Department</label>
                                            <select style={{ width: '100%', backgroundColor: slate50, border: `1px solid ${slate200}`, borderRadius: '12px', padding: '16px', fontSize: '12px', fontWeight: 700, outline: 'none' }}>
                                                <option>Election Commission</option>
                                                <option>Administration</option>
                                                <option>Constituency Security</option>
                                            </select>
                                        </div>
                                    </>
                                )}
                                <FlatField label="Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" value={passwordInput} onChange={setPasswordInput} />
                                <FlatField label="Confirm Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" />

                                <button type="submit" disabled={loading} style={{
                                    width: '100%',
                                    backgroundColor: loading ? slate400 : navy,
                                    color: white,
                                    padding: '16px',
                                    marginTop: '16px',
                                    borderRadius: '16px',
                                    fontWeight: 900,
                                    fontSize: '10px',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.3em',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '12px',
                                    border: 'none',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                    boxShadow: loading ? 'none' : '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                                }}>
                                    {loading ? 'Processing...' : (userType === 'booth' ? 'Register Booth' : 'Register Official')} {!loading && <ArrowRight size={16} color={gold} />}
                                </button>
                            </div>
                        )}

                        {view === 'login' && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                {userType === 'booth' ? (
                                    <>
                                        <FlatField label="Official Name" icon={<User size={16} />} placeholder="Enter registered name" value={nameInput} onChange={setNameInput} />
                                        <FlatField label="Booth ID" icon={<BadgeCheck size={16} />} placeholder="Enter unique Booth #" value={boothIdInput} onChange={setBoothIdInput} />
                                    </>
                                ) : (
                                    <FlatField label="Gov Official ID" icon={<ShieldCheck size={16} />} placeholder="Enter ID" value={nameInput} onChange={setNameInput} />
                                )}
                                <FlatField label="Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" value={passwordInput} onChange={setPasswordInput} />

                                <button type="submit" disabled={loading} style={{
                                    width: '100%',
                                    backgroundColor: loading ? slate400 : navy,
                                    color: white,
                                    padding: '16px',
                                    marginTop: '32px',
                                    borderRadius: '16px',
                                    fontWeight: 900,
                                    fontSize: '10px',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.3em',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '12px',
                                    border: 'none',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s ease'
                                }}>
                                    {loading ? 'Authorizing...' : 'Authorize Login'} {!loading && <ArrowRight size={16} color={gold} />}
                                </button>
                            </div>
                        )}
                    </form>

                    <footer style={{ marginTop: '48px', textAlign: 'center' }}>
                        <p style={{ fontSize: '10px', color: slate400, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', lineHeight: 1.6 }}>
                            © 2026 <img src={logo} alt="Logo" style={{ height: '14px', verticalAlign: 'middle', margin: '0 4px', filter: 'brightness(0)' }} /> • National Data Network <br />
                            <span style={{ color: gold }}>Secure Intelligence Node</span>
                        </p>
                    </footer>
                </div>
            </div>

        </div>
    );
}

function FlatField({ label, icon, placeholder, type = "text", value, onChange }) {
    const slate200 = "#e2e8f0";
    const slate50 = "#f8fafc";
    const slate300 = "#cbd5e1";
    const slate400 = "#94a3b8";

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '9px', fontWeight: 900, color: slate400, textTransform: 'uppercase', letterSpacing: '0.1em', marginLeft: '4px' }}>{label}</label>
            <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: slate300 }}>{icon}</div>
                <input
                    type={type}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    style={{
                        width: '100%',
                        backgroundColor: slate50,
                        border: `1px solid ${slate200}`,
                        borderRadius: '12px',
                        padding: '16px 16px 16px 48px',
                        fontSize: '12px',
                        fontWeight: 700,
                        outline: 'none',
                        transition: 'border-color 0.2s ease'
                    }}
                    placeholder={placeholder}
                    onFocus={(e) => e.target.style.borderColor = "#D4AF37"}
                    onBlur={(e) => e.target.style.borderColor = slate200}
                />
            </div>
        </div>
    );
}