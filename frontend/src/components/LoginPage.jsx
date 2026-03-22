import React, { useState } from 'react';
import {
    ShieldCheck, User, Lock, Building2, MapPin,
    ArrowRight, Globe, BadgeCheck
} from 'lucide-react';

export default function LoginPage() {
    const [view, setView] = useState('signup'); // 'signup' or 'login'
    const [userType, setUserType] = useState('booth'); // 'booth' or 'official'

    const navy = "bg-[#0f172a]";
    const goldText = "text-[#D4AF37]";
    const goldBg = "bg-[#D4AF37]";

    return (
        <div className="flex h-screen w-full bg-white font-sans overflow-hidden">

            {/* LEFT SIDE: Solid Navy Branding */}
            <div className={`hidden lg:flex w-1/2 ${navy} flex-col justify-center px-20 relative`}>
                <div className="max-w-md relative z-10">

                    {/* LOGO REMOVED & TEXT REALIGNED */}
                    <div className="flex flex-col mb-12">
                        <span className={`font-black text-4xl tracking-tighter leading-none uppercase ${goldText}`}>
                            Civix AI
                        </span>
                        <span className="text-slate-500 text-[10px] font-black tracking-[0.4em] mt-2 uppercase border-t border-slate-800 pt-2 w-fit">
                            Booth Intelligence
                        </span>
                    </div>

                    <h1 className="text-white text-5xl font-black tracking-tight mb-6 leading-none uppercase">
                        National <br /> Agency Portal
                    </h1>

                    <div className={`h-1.5 w-20 ${goldBg} mb-10`} />

                    <p className="text-slate-400 text-lg font-medium leading-relaxed max-w-sm">
                        Dedicated infrastructure for Booth Officials and Government Administration.
                        Real-time complaint logging and encrypted data relay.
                    </p>
                </div>
            </div>

            {/* RIGHT SIDE: Form Portal */}
            <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 sm:px-16 lg:px-24 bg-white overflow-y-auto">
                <div className="max-w-md w-full mx-auto py-12">

                    <div className="mb-12 text-right">
                        <button
                            onClick={() => setView(view === 'login' ? 'signup' : 'login')}
                            className="text-slate-400 text-[10px] font-black uppercase tracking-widest hover:text-[#0f172a] transition-colors"
                        >
                            {view === 'login' ? 'Register New Access →' : 'Already Authorized? Sign In →'}
                        </button>
                    </div>

                    <div className="mb-10">
                        <h2 className="text-3xl font-black text-[#0f172a] tracking-tight uppercase">
                            {view === 'login' ? 'Portal Login' : 'System Registration'}
                        </h2>
                        <p className="text-slate-400 text-[10px] font-black mt-2 uppercase tracking-[0.2em]">
                            Authorized Access Only
                        </p>
                    </div>

                    <div className="flex border-2 border-slate-100 rounded-2xl mb-10 p-1.5 bg-slate-50">
                        <button
                            onClick={() => setUserType('booth')}
                            className={`flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl text-[10px] font-black tracking-widest transition-all ${userType === 'booth' ? `${navy} text-white shadow-xl` : 'text-slate-400'}`}
                        >
                            <MapPin size={14} className={userType === 'booth' ? goldText : ''} /> BOOTH
                        </button>
                        <button
                            onClick={() => setUserType('official')}
                            className={`flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl text-[10px] font-black tracking-widest transition-all ${userType === 'official' ? `${navy} text-white shadow-xl` : 'text-slate-400'}`}
                        >
                            <ShieldCheck size={14} className={userType === 'official' ? goldText : ''} /> OFFICIAL
                        </button>
                    </div>

                    <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
                        {view === 'signup' && (
                            <div className="space-y-5 animate-in fade-in duration-300">
                                {userType === 'booth' ? (
                                    <>
                                        <FlatField label="Name of the Official" icon={<User size={16} />} placeholder="In-charge Full Name" />
                                        <FlatField label="Booth ID" icon={<BadgeCheck size={16} />} placeholder="Enter unique Booth #" />
                                        <FlatField label="State" icon={<Globe size={16} />} placeholder="Enter State / Union Territory" />
                                    </>
                                ) : (
                                    <>
                                        <FlatField label="Gov Official ID" icon={<ShieldCheck size={16} />} placeholder="GOV-XXXX-XXXX" />
                                        <div className="space-y-1.5">
                                            <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">Department</label>
                                            <select className="w-full bg-slate-50 border border-slate-200 rounded-xl py-4 px-4 text-xs font-bold outline-none focus:border-[#D4AF37]">
                                                <option>Election Commission</option>
                                                <option>Administration</option>
                                                <option>Constituency Security</option>
                                            </select>
                                        </div>
                                    </>
                                )}
                                <FlatField label="Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" />
                                <FlatField label="Confirm Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" />

                                <button className={`w-full ${navy} text-white py-4 mt-4 rounded-2xl font-black text-[10px] uppercase tracking-[0.3em] flex items-center justify-center gap-3 hover:bg-black transition-all shadow-lg`}>
                                    {userType === 'booth' ? 'Register Booth' : 'Register Official'} <ArrowRight size={16} className={goldText} />
                                </button>
                            </div>
                        )}

                        {view === 'login' && (
                            <div className="space-y-5 animate-in fade-in duration-300">
                                {userType === 'booth' ? (
                                    <FlatField label="Official Name" icon={<User size={16} />} placeholder="Enter registered name" />
                                ) : (
                                    <FlatField label="Gov Official ID" icon={<ShieldCheck size={16} />} placeholder="Enter ID" />
                                )}
                                <FlatField label="Password" icon={<Lock size={16} />} placeholder="••••••••" type="password" />

                                <button className={`w-full ${navy} text-white py-4 mt-8 rounded-2xl font-black text-[10px] uppercase tracking-[0.3em] flex items-center justify-center gap-3 hover:bg-black transition-all`}>
                                    Authorize Login <ArrowRight size={16} className={goldText} />
                                </button>
                            </div>
                        )}
                    </form>

                    <footer className="mt-12 text-center">
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-relaxed">
                            © 2026 Civix AI • National Data Network <br />
                            <span className={goldText}>Secure Intelligence Node</span>
                        </p>
                    </footer>
                </div>
            </div>

        </div>
    );
}

function FlatField({ label, icon, placeholder, type = "text" }) {
    return (
        <div className="space-y-1.5">
            <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">{label}</label>
            <div className="relative">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300">{icon}</div>
                <input
                    type={type}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl py-4 pl-12 pr-4 text-xs font-bold outline-none focus:border-[#D4AF37] placeholder:text-slate-200 transition-all"
                    placeholder={placeholder}
                />
            </div>
        </div>
    );
}