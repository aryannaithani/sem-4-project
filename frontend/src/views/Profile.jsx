import { useEffect, useState } from 'react';
import { getProfile, getLearningProfile } from '../api';
import { GitBranch, Clock, ShieldCheck, Activity } from 'lucide-react';
import { clsx } from 'clsx';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [learningProfile, setLearningProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([getProfile(), getLearningProfile()])
            .then(([p, lp]) => {
                setProfile(p);
                setLearningProfile(lp);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="muted">Loading profile...</div>;

    if (!profile || !learningProfile) {
        return (
            <div className="panel p-6">
                <h2 className="title-lg">Profile unavailable</h2>
                <p className="muted mt-2">Could not load profile data from backend.</p>
                <button onClick={() => window.location.reload()} className="btn mt-4">Try again</button>
            </div>
        );
    }

    // Prepare Skill Radar Chart Data
    // We'll pick the top 6-8 skills and map "beginner"=33 "intermediate"=66 "advanced"=100
    const topSkills = Object.entries(profile.skills)
        .filter(([, level]) => level !== 'none' && level !== 'absent')
        .slice(0, 6);

    while (topSkills.length > 0 && topSkills.length < 6) {
        topSkills.push([`Placeholder ${topSkills.length}`, "none"]);
    }

    const levelToNum = (level) => {
        if (level === 'advanced') return 100;
        if (level === 'intermediate') return 60;
        if (level === 'beginner') return 25;
        return 0;
    };

    // Calculate radar points
    const drawRadar = (radius, cx, cy) => {
        if (topSkills.length === 0) return '';
        const angleStep = (Math.PI * 2) / topSkills.length;
        const pts = topSkills.map((st, i) => {
            const val = levelToNum(st[1]) / 100;
            const r = radius * val;
            const x = cx + r * Math.sin(i * angleStep);
            const y = cy - r * Math.cos(i * angleStep);
            return `${x},${y}`;
        }).join(' ');
        return pts;
    };

    const drawGrid = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        return Array.from({ length: 4 }).map((_, level) => {
            const r = radius * ((level + 1) / 4);
            const angleStep = (Math.PI * 2) / numSides;
            const pts = Array.from({ length: numSides }).map((_, i) => {
                const x = cx + r * Math.sin(i * angleStep);
                const y = cy - r * Math.cos(i * angleStep);
                return `${x},${y}`;
            }).join(' ');
            return <polygon key={level} points={pts} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />;
        });
    };

    const drawAxes = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        const angleStep = (Math.PI * 2) / numSides;
        return Array.from({ length: numSides }).map((_, i) => {
            const x = cx + radius * Math.sin(i * angleStep);
            const y = cy - radius * Math.cos(i * angleStep);
            return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />;
        });
    };

    const renderLabels = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        const angleStep = (Math.PI * 2) / numSides;
        return topSkills.map(([skill], i) => {
            const x = cx + (radius + 20) * Math.sin(i * angleStep);
            const y = cy - (radius + 20) * Math.cos(i * angleStep);
            return (
                <text key={i} x={x} y={y} fontSize="10" fill="#94a3b8" textAnchor="middle" dominantBaseline="middle">
                    {skill.length > 15 ? skill.substring(0, 12) + '...' : skill}
                </text>
            );
        });
    }

  return (
        <div>
            <header className="mb-6 flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-white text-black flex items-center justify-center text-xl font-bold">
                    {profile.name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                    <h1 className="title-xl">{profile.name}&apos;s Digital Twin</h1>
                    <p className="muted flex items-center gap-2 mt-1 text-sm">
                        Goal: {profile.goal}
                        {profile.github && <><span>|</span> <GitBranch size={14} /> {profile.github}</>}
                    </p>
                </div>
            </header>

            <div className="grid lg:grid-cols-3 gap-4">
                <div className="panel p-5 space-y-3">
                    <h2 className="title-lg">Learning Metrics</h2>
                    <div className="panel-soft p-4">
                        <div className="text-xs muted mb-1 flex items-center gap-2"><Clock size={14} /> Velocity</div>
                        <div className="font-bold text-2xl">{learningProfile.learning_velocity}<span className="text-xs muted ml-1">tasks/day</span></div>
                    </div>
                    <div className="panel-soft p-4">
                        <div className="text-xs muted mb-1 flex items-center gap-2"><Activity size={14} /> Consistency</div>
                        <div className="font-bold text-2xl">{learningProfile.consistency_score}%</div>
                    </div>
                    <div className="panel-soft p-4">
                        <div className="text-xs muted mb-1 flex items-center gap-2"><ShieldCheck size={14} /> Complexity index</div>
                        <div className="font-bold text-2xl">{learningProfile.project_complexity_index}</div>
                    </div>
                </div>

                <div className="lg:col-span-2 panel p-6">
                    <h2 className="title-lg mb-3">Skill Profile Shape</h2>
                    {topSkills.length >= 3 ? (
                        <div className="w-full h-80 max-w-sm">
                            <svg viewBox="0 0 300 300" className="w-full h-full overflow-visible">
                                {drawGrid(100, 150, 150, topSkills.length)}
                                {drawAxes(100, 150, 150, topSkills.length)}
                                <polygon points={drawRadar(100, 150, 150)} fill="rgba(255,255,255,0.12)" stroke="#fff" strokeWidth="2" />
                                {renderLabels(100, 150, 150, topSkills.length)}
                                {topSkills.map((st, i) => {
                                    const val = levelToNum(st[1]) / 100;
                                    const r = 100 * val;
                                    const angleStep = (Math.PI * 2) / topSkills.length;
                                    const x = 150 + r * Math.sin(i * angleStep);
                                    const y = 150 - r * Math.cos(i * angleStep);
                                    return <circle key={i} cx={x} cy={y} r="3" fill="#ffffff" />;
                                })}
                            </svg>
                        </div>
                    ) : (
                        <div className="muted text-sm">Need at least 3 skills to show radar profile.</div>
                    )}
                </div>
            </div>

            <div className="mt-4 panel p-5">
                <h2 className="title-lg mb-3">Skill Inventory</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(profile.skills).filter(([, l]) => l !== 'none' && l !== 'absent').map(([skill, level], idx) => (
                        <div key={idx} className="panel-soft p-3 rounded-lg flex flex-col gap-2">
                            <span className="font-semibold text-sm">{skill}</span>
                            <div className="flex items-center gap-2">
                                <span className={clsx(
                                    "w-2 h-2 rounded-full",
                                    level === 'beginner' ? 'bg-[#777]' :
                                        level === 'intermediate' ? 'bg-[#bbb]' :
                                            'bg-[#fff]'
                                )}></span>
                                <span className="text-xs muted capitalize">{level}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Profile;
