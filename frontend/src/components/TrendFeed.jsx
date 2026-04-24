import React, { useEffect, useState } from 'react';
import { getTrends } from '../api';
import { Flame, CheckCircle, Circle, AlertCircle } from 'lucide-react';

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
            <div className="card p-6 h-full border-slate-800">
                <div className="skeleton w-1/3 h-6 mb-6"></div>
                <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="skeleton w-full h-10"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="card p-0 overflow-hidden h-full flex flex-col border-slate-800">
            <div className="p-5 border-b border-white/5 bg-white/5 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-orange-500/20 flex items-center justify-center text-orange-500">
                    <Flame size={18} />
                </div>
                <h3 className="font-bold text-white">Live Industry Trends</h3>
            </div>

            <div className="flex-1 overflow-y-auto p-2 scroll-area">
                <div className="space-y-1">
                    {trends.slice(0, 8).map((trend, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-colors">
                            <div className="flex items-center gap-3">
                                <span className="text-slate-600 font-bold text-xs w-4">{idx + 1}.</span>
                                <span className="font-medium text-slate-200 text-sm">{trend.name}</span>
                            </div>

                            {trend.already_known ? (
                                <div className="flex items-center gap-1.5" data-tooltip="You already know this skill">
                                    <CheckCircle size={14} className="text-emerald-500" />
                                    <span className="text-[10px] font-bold uppercase text-emerald-500 tracking-wider">Known</span>
                                </div>
                            ) : trend.relevance === 'high' ? (
                                <div className="flex items-center gap-1.5" data-tooltip="High relevance gap for your goal">
                                    <AlertCircle size={14} className="text-orange-500" />
                                    <span className="text-[10px] font-bold uppercase text-orange-500 tracking-wider">Gap</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-1.5" data-tooltip="Building towards this">
                                    <Circle size={14} className="text-blue-500" />
                                    <span className="text-[10px] font-bold uppercase text-blue-500 tracking-wider">Building</span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
            <div className="p-4 bg-white/5 text-xs text-slate-500 text-center border-t border-white/5">
                Top matched skills in job postings & GitHub.
            </div>
        </div>
    );
};

export default TrendFeed;
