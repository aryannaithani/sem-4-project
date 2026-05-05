import { useEffect, useState } from 'react';
import { getProfile, getAnalytics } from '../api';
import { ArrowRight } from 'lucide-react';
import TrendFeed from '../components/TrendFeed';

const Dashboard = ({ setCurrentView }) => {
    const [profile, setProfile] = useState(null);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [pData, aData] = await Promise.all([
                    getProfile(),
                    getAnalytics()
                ]);
                setProfile(pData);
                setAnalytics(aData);
            } catch (error) {
                console.error("Failed to load dashboard data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="muted">Loading dashboard...</div>;

    if (!profile) {
        return (
            <div className="panel p-6">
                <h2 className="title-lg">Data unavailable</h2>
                <p className="muted mt-2">Backend appears disconnected. Start server and retry.</p>
                <button onClick={() => window.location.reload()} className="btn mt-4">Try again</button>
            </div>
        );
    }

    return (
        <div>
            <header className="mb-6">
                <h1 className="title-xl">Welcome back, {profile.name}</h1>
                <p className="muted mt-2">Focused roadmap and outcomes for your goal: {profile.goal}</p>
            </header>

            <div className="grid-cards md:grid-cols-3 mb-6">
                <div className="panel kpi">
                    <div className="muted text-sm">Career progress</div>
                    <div className="kpi-value">{profile.career_progress}%</div>
                    <div className="progress-track mt-3">
                        <div className="progress-fill" style={{ width: `${profile.career_progress}%` }} />
                    </div>
                </div>
                <div className="panel kpi">
                    <div className="muted text-sm">Current stage</div>
                    <div className="kpi-value text-2xl">{profile.current_stage || 'Unknown'}</div>
                    <div className="muted mt-2 text-sm">Stage progress: {profile.stage_progress || 0}%</div>
                </div>
                <div className="panel kpi">
                    <div className="muted text-sm">Readiness</div>
                    <div className="kpi-value">{analytics?.real_world_readiness ?? 0}%</div>
                    <div className="muted mt-2 text-sm">Trend alignment: {analytics?.trend_alignment_score ?? 0}%</div>
                </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="panel p-6 md:col-span-2">
                    <h2 className="title-lg">Today&apos;s Direction</h2>
                    <p className="muted mt-2">
                        Continue disciplined, project-based execution. Your mentorship plan is tuned for higher-study learners and career-ready output.
                    </p>
                    <div className="flex gap-3 mt-6 flex-wrap">
                        <button onClick={() => setCurrentView('tasks')} className="btn btn-primary">
                            Open task board <ArrowRight size={16} />
                        </button>
                        <button onClick={() => setCurrentView('chat')} className="btn">
                            Ask mentor
                        </button>
                    </div>
                </div>
                <button onClick={() => setCurrentView('profile')} className="panel p-6 text-left hover:border-[#4a4a50] transition-colors">
                    <h3 className="title-lg">Digital twin profile</h3>
                    <p className="muted mt-2">Review skill depth and learning characteristics.</p>
                    <div className="mt-4 chip inline-flex">Open profile</div>
                </button>
            </div>

            <div className="grid lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 panel p-6">
                    <h3 className="title-lg">Analytics Snapshot</h3>
                    <div className="mt-4 grid md:grid-cols-2 gap-3">
                        <div className="panel-soft p-4">
                            <div className="muted text-xs uppercase">Trajectory</div>
                            <div className="mt-1 font-semibold capitalize">{analytics?.career_trajectory || 'Unknown'}</div>
                        </div>
                        <div className="panel-soft p-4">
                            <div className="muted text-xs uppercase">Goal</div>
                            <div className="mt-1 font-semibold">{profile.goal}</div>
                        </div>
                    </div>
                </div>
                <TrendFeed />
            </div>
        </div>
    );
};

export default Dashboard;
