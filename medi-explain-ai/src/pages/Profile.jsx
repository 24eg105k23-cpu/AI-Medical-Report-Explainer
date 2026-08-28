import React, { useState } from 'react';
import { User, Mail, Phone, Globe, Bell, Save, CheckCircle, Clock, Pill, Plus, Trash2, Sun, Cloud, Moon } from 'lucide-react';

const Profile = () => {
  const [saved, setSaved] = useState(false);
  const [language, setLanguage] = useState('en');
  const [activeTab, setActiveTab] = useState('profile');
  const [profile, setProfile] = useState({
    name: 'Raj Sharma',
    email: 'raj.sharma@example.com',
    phone: '9876543210',
    language: 'English',
    notifications: true
  });

  const [reminders, setReminders] = useState([
    { id: 1, medicine: 'Atorvastatin 10mg', time: 'Morning', active: true },
    { id: 2, medicine: 'Paracetamol 500mg', time: 'Afternoon', active: true },
    { id: 3, medicine: 'Paracetamol 500mg', time: 'Night', active: false }
  ]);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const toggleReminder = (id) => {
    setReminders(prev => prev.map(r => r.id === id ? { ...r, active: !r.active } : r));
  };

  const deleteReminder = (id) => {
    setReminders(prev => prev.filter(r => r.id !== id));
  };

  const timeIcons = {
    'Morning': <Sun size={18} />,
    'Afternoon': <Cloud size={18} />,
    'Night': <Moon size={18} />
  };

  // Mock Hindi translations
  const translations = {
    en: {
      title: 'Profile Settings',
      remindersTitle: 'Medicine Reminders',
      name: 'Full Name',
      email: 'Email',
      phone: 'Phone Number',
      lang: 'Preferred Language',
      notif: 'Notifications',
      save: 'Save Changes',
      saved: 'Changes Saved!',
      disclaimer: 'Reminders are a UI demonstration only and do not send real notifications.'
    },
    hi: {
      title: 'प्रोफ़ाइल सेटिंग्स',
      remindersTitle: 'दवा अनुस्मारक',
      name: 'पूरा नाम',
      email: 'ईमेल',
      phone: 'फोन नंबर',
      lang: 'पसंदीदा भाषा',
      notif: 'सूचनाएं',
      save: 'परिवर्तन सहेजें',
      saved: 'परिवर्तन सहेजे गए!',
      disclaimer: 'रिमाइंडर केवल एक UI प्रदर्शन हैं और वास्तविक सूचनाएं नहीं भेजते।'
    }
  };

  const t = translations[language];

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem', maxWidth: '800px' }}>
      {/* Language Selector */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <Globe size={18} color="var(--color-text-muted)" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-family)',
              fontSize: '0.875rem',
              backgroundColor: 'white',
              outline: 'none'
            }}
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--color-border)' }}>
        <button
          onClick={() => setActiveTab('profile')}
          style={{
            padding: '0.75rem 1.5rem',
            background: 'none',
            border: 'none',
            fontWeight: activeTab === 'profile' ? 600 : 400,
            color: activeTab === 'profile' ? 'var(--color-primary)' : 'var(--color-text-muted)',
            borderBottom: activeTab === 'profile' ? '2px solid var(--color-primary)' : '2px solid transparent',
            cursor: 'pointer',
            fontFamily: 'var(--font-family)',
            fontSize: '1rem'
          }}
        >
          <User size={18} style={{ marginRight: '0.5rem', verticalAlign: 'text-bottom' }} />
          {t.title}
        </button>
        <button
          onClick={() => setActiveTab('reminders')}
          style={{
            padding: '0.75rem 1.5rem',
            background: 'none',
            border: 'none',
            fontWeight: activeTab === 'reminders' ? 600 : 400,
            color: activeTab === 'reminders' ? 'var(--color-primary)' : 'var(--color-text-muted)',
            borderBottom: activeTab === 'reminders' ? '2px solid var(--color-primary)' : '2px solid transparent',
            cursor: 'pointer',
            fontFamily: 'var(--font-family)',
            fontSize: '1rem'
          }}
        >
          <Clock size={18} style={{ marginRight: '0.5rem', verticalAlign: 'text-bottom' }} />
          {t.remindersTitle}
        </button>
      </div>

      {activeTab === 'profile' && (
        <div className="card">
          {/* Avatar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '2rem', fontWeight: 700, flexShrink: 0 }}>
              RS
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>{profile.name}</h2>
              <p style={{ color: 'var(--color-text-muted)' }}>{profile.email}</p>
            </div>
          </div>

          {/* Form */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {[
              { label: t.name, name: 'name', icon: <User size={18} />, type: 'text' },
              { label: t.email, name: 'email', icon: <Mail size={18} />, type: 'email' },
              { label: t.phone, name: 'phone', icon: <Phone size={18} />, type: 'tel' }
            ].map(field => (
              <div key={field.name}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.375rem', color: 'var(--color-text-main)' }}>{field.label}</label>
                <div style={{ position: 'relative' }}>
                  <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }}>{field.icon}</span>
                  <input
                    type={field.type}
                    value={profile[field.name]}
                    onChange={(e) => setProfile(prev => ({ ...prev, [field.name]: e.target.value }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem 0.75rem 3rem',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem',
                      fontFamily: 'var(--font-family)',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>
            ))}

            {/* Notification Toggle */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Bell size={18} color="var(--color-text-muted)" />
                <span style={{ fontWeight: 500 }}>{t.notif}</span>
              </div>
              <button
                onClick={() => setProfile(prev => ({ ...prev, notifications: !prev.notifications }))}
                style={{
                  width: '48px',
                  height: '28px',
                  borderRadius: '9999px',
                  border: 'none',
                  backgroundColor: profile.notifications ? 'var(--color-primary)' : 'var(--color-border)',
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
              >
                <span style={{
                  position: 'absolute',
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  backgroundColor: 'white',
                  top: '3px',
                  left: profile.notifications ? '23px' : '3px',
                  transition: 'left 0.2s',
                  boxShadow: 'var(--shadow-sm)'
                }}></span>
              </button>
            </div>

            <button className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} onClick={handleSave}>
              {saved ? <><CheckCircle size={20} /> {t.saved}</> : <><Save size={20} /> {t.save}</>}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'reminders' && (
        <div>
          <div className="card" style={{ marginBottom: '1rem', backgroundColor: 'var(--color-primary-light)', borderLeft: '4px solid var(--color-primary)' }}>
            <p style={{ color: 'var(--color-primary-dark)', fontSize: '0.9375rem' }}>{t.disclaimer}</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {reminders.map(rem => (
              <div key={rem.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: rem.active ? 1 : 0.6, flexWrap: 'wrap', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', padding: '0.75rem', borderRadius: 'var(--radius-lg)' }}>
                    {timeIcons[rem.time] || <Pill size={18} />}
                  </div>
                  <div>
                    <h3 style={{ fontWeight: 600 }}>{rem.medicine}</h3>
                    <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{rem.time}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <button
                    onClick={() => toggleReminder(rem.id)}
                    style={{
                      width: '48px',
                      height: '28px',
                      borderRadius: '9999px',
                      border: 'none',
                      backgroundColor: rem.active ? 'var(--color-success)' : 'var(--color-border)',
                      position: 'relative',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <span style={{
                      position: 'absolute',
                      width: '22px',
                      height: '22px',
                      borderRadius: '50%',
                      backgroundColor: 'white',
                      top: '3px',
                      left: rem.active ? '23px' : '3px',
                      transition: 'left 0.2s',
                      boxShadow: 'var(--shadow-sm)'
                    }}></span>
                  </button>
                  <button className="btn" style={{ padding: '0.375rem', background: 'none', border: 'none', color: 'var(--color-text-light)' }} onClick={() => deleteReminder(rem.id)}>
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}

            <button className="btn btn-secondary" style={{ width: '100%', marginTop: '0.5rem' }}>
              <Plus size={20} /> Add Reminder
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
