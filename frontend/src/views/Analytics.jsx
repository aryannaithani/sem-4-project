import { useEffect, useState } from 'react';
import { getAnalytics } from '../api';
import { CheckCircle, AlertCircle } from 'lucide-react';

const Analytics = () => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getAnalytics()
            .then(data => setAnalytics(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="muted">Loading analytics...</div>;

    if (!analytics) {
        return (
            <div className="panel p-6">
                <h2 className="title-lg">Analytics unavailable</h2>
                <p className="muted mt-2">Could not retrieve analytics data from backend.</p>
                <button onClick={() => window.location.reload()} className="btn mt-4">Try again</button>
            </div>
        );
    }

    // Prepare history data for simple SVG chart
    const history = analytics.readiness_history || [];
    const minVal = Math.min(...history.map(h => h.score), 0);
    const maxVal = 100;

    // Scale history to 0-1 range for plotting
    const pts = history.map((h, i) => {
        const x = history.length > 1 ? (i / (history.length - 1)) * 100 : 50;
        const y = 100 - ((h.score - minVal) / ((maxVal - minVal) || 1)) * 100;
        return `${x},${y}`;
    }).join(' ');

    return (
        <div>
            <header className="mb-6">
                <h1 className="title-xl">Career Analytics</h1>
                <p className="muted mt-2">Quantitative perspective on progress and skill maturity.</p>
            </header>

            <div className="grid-cards md:grid-cols-3 mb-4">
                <div className="panel kpi">
                    <div className="muted text-xs uppercase">Readiness</div>
                    <div className="kpi-value">{analytics.real_world_readiness}%</div>
                </div>
                <div className="panel kpi">
                    <div className="muted text-xs uppercase">Trajectory</div>
                    <div className="kpi-value text-2xl capitalize">{analytics.career_trajectory}</div>
                </div>
                <div className="panel kpi">
                    <div className="muted text-xs uppercase">Trend alignment</div>
                    <div className="kpi-value">{analytics.trend_alignment_score}%</div>
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 panel p-6">
                    <h2 className="title-lg mb-4">Readiness Trajectory</h2>
                    {history.length > 1 ? (
                        <div className="w-full h-48 border border-[#24242a] rounded">
                            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                                <polyline
                                    fill="none"
                                    stroke="#ffffff"
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    points={pts}
                                />
                                {history.map((h, i) => {
                                    const x = (i / (history.length - 1)) * 100;
                                    const y = 100 - ((h.score - minVal) / ((maxVal - minVal) || 1)) * 100;
                                    return (
                                        <circle
                                            key={i}
                                            cx={x}
                                            cy={y}
                                            r="2.5"
                                            fill="#0d0d10"
                                            stroke="#ffffff"
                                            strokeWidth="1.5"
                                        >
                                            <title>{h.date.substring(0, 10)}: {h.score}%</title>
                                        </circle>
                                    );
                                })}
                            </svg>
                        </div>
                    ) : (
                        <div className="h-48 flex items-center justify-center muted text-sm">
                            Need more data points to show trajectory. Keep completing tasks!
                        </div>
                    )}
                </div>

                <div className="panel p-6">
                    <h2 className="title-lg mb-4">Skill Depth</h2>
                    <div className="space-y-3 max-h-[20rem] overflow-auto">
                        {Object.entries(analytics.skill_depth_breakdown || {}).length === 0 ? (
                            <p className="muted text-sm">No skills tracked yet.</p>
                        ) : (
                            Object.entries(analytics.skill_depth_breakdown).map(([skill, info], idx) => (
                                <div key={idx} className="border-b border-[#222229] pb-2">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="font-semibold">{skill}</span>
                                        <span className="chip">{info.depth}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-xs muted">
                                        <span className="capitalize">{info.level}</span>
                                        {info.confidence ? <span>Conf: {info.confidence}/5</span> : <span>No conf</span>}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            <div className="mt-4 grid md:grid-cols-2 gap-4">
                <div className="panel p-6 max-h-64 overflow-y-auto">
                    <h3 className="text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                        <CheckCircle size={16} /> Top Strengths
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {analytics.top_strength_skills?.length > 0 ? (
                            analytics.top_strength_skills.map((s, i) => (
                                <span key={i} className="chip">
                                    {s}
                                </span>
                            ))
                        ) : (
                            <span className="muted text-sm">No deep strengths identified yet.</span>
                        )}
                    </div>
                </div>

                <div className="panel p-6 max-h-64 overflow-y-auto">
                    <h3 className="text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                        <AlertCircle size={16} /> Highest Priority Gaps
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {analytics.highest_priority_gaps?.length > 0 ? (
                            analytics.highest_priority_gaps.map((s, i) => (
                                <span key={i} className="chip">
                                    {s}
                                </span>
                            ))
                        ) : (
                            <span className="muted text-sm">No critical gaps identified right now.</span>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
};

export default Analytics;
