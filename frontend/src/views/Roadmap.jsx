import { useEffect, useState } from 'react';
import { getFullRoadmap } from '../api';
import { CheckCircle, ArrowRight, Lock } from 'lucide-react';

const Roadmap = ({ setCurrentView }) => {
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getFullRoadmap()
            .then(data => setRoadmap(data))
            .catch(err => console.error("Error fetching full roadmap:", err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="muted">Loading roadmap...</div>;

    if (!roadmap || !roadmap.stages) {
        return (
            <div className="panel p-6">
                <h2 className="title-lg">Roadmap unavailable</h2>
                <p className="muted mt-2">Could not load roadmap data from backend.</p>
                <button onClick={() => window.location.reload()} className="btn mt-4">Try again</button>
            </div>
        );
    }

    return (
        <div>
            <header className="mb-6">
                <div>
                    <h1 className="title-xl">Roadmap</h1>
                    <p className="muted mt-2">Structured path to {roadmap.goal}</p>
                </div>
            </header>

            <div className="space-y-4">
                {roadmap.stages.map((stage, idx) => {
                    const isCurrent = stage.name === roadmap.current_stage;

                    return (
                        <article key={idx} className={`panel p-5 ${isCurrent ? 'border-[#f0f0f0]' : ''}`}>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h2 className="title-lg flex items-center gap-2">
                                            {stage.name}
                                            {isCurrent && <span className="chip">Active</span>}
                                        </h2>
                                        <p className="muted text-sm">
                                            {stage.learned} of {stage.total} skills mastered
                                        </p>
                                    </div>
                                    <div className="font-bold">{stage.progress}%</div>
                                </div>

                                <div className="progress-track mt-4 mb-4">
                                    <div className="progress-fill" style={{ width: `${stage.progress}%` }} />
                                </div>

                                <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2">
                                    {stage.skills.map((skill, sIdx) => {
                                        const known = skill.level !== 'none' && skill.level !== 'absent';
                                        return (
                                            <div key={sIdx} className={`p-2 rounded border text-sm flex items-center gap-2 ${known ? 'border-white text-white' : 'border-[#25252a] text-[#8d8e95]'}`}>
                                                {known ? <CheckCircle size={14} /> : <Lock size={14} />}
                                                <span className="truncate">{skill.name}</span>
                                            </div>
                                        );
                                    })}
                                </div>

                                {isCurrent && (
                                    <div className="mt-5 flex justify-end">
                                        <button
                                            onClick={() => setCurrentView && setCurrentView('tasks')}
                                            className="btn btn-primary"
                                        >
                                            Generate tasks <ArrowRight size={14} />
                                        </button>
                                    </div>
                                )}
                        </article>
                    );
                })}
            </div>
        </div>
    );
};

export default Roadmap;
