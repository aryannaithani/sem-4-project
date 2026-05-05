import { useEffect, useState } from 'react';
import { getTrends } from '../api';
import { CheckCircle, Circle, AlertCircle } from 'lucide-react';

const TrendFeed = () => {
    const [trends, setTrends] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getTrends()
            .then(data => setTrends(data.trends || []))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="panel p-5">
                <div className="text-sm muted">Loading trends...</div>
                <div className="mt-4 space-y-2">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-8 rounded bg-[#1a1a1f]" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="panel h-full">
            <div className="p-5 border-b border-[#232328]">
                <h3 className="font-bold">Industry Trend Signals</h3>
                <p className="text-xs muted mt-1">Skills from market demand and repositories</p>
            </div>

            <div className="p-3 space-y-2">
                <div className="space-y-1">
                    {trends.slice(0, 8).map((trend, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-[#232328] bg-[#101014]">
                            <div className="flex items-center gap-3">
                                <span className="text-[#6f7077] font-bold text-xs w-4">{idx + 1}.</span>
                                <span className="font-medium text-sm">{trend.name}</span>
                            </div>

                            {trend.already_known ? (
                                <div className="flex items-center gap-1.5" data-tooltip="You already know this skill">
                                    <CheckCircle size={14} className="text-white" />
                                    <span className="text-[10px] font-bold uppercase text-white tracking-wider">Known</span>
                                </div>
                            ) : trend.relevance === 'high' ? (
                                <div className="flex items-center gap-1.5" data-tooltip="High relevance gap for your goal">
                                    <AlertCircle size={14} className="text-[#cfcfd3]" />
                                    <span className="text-[10px] font-bold uppercase text-[#cfcfd3] tracking-wider">Gap</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-1.5" data-tooltip="Building towards this">
                                    <Circle size={14} className="text-[#8d8e95]" />
                                    <span className="text-[10px] font-bold uppercase text-[#8d8e95] tracking-wider">Build</span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TrendFeed;
