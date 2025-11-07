// 圖表配置模組
window.Charts = {
    // 通用圖表配置 - 深色主題
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: true,
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        },
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: '#E5E7EB',  
                    font: {
                        size: 13,
                        family: "'Inter', 'Segoe UI', sans-serif"
                    },
                    padding: 15,
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            title: {
                color: '#F9FAFB',  // 亮白色
                font: {
                    size: 16,
                    weight: 'bold',
                    family: "'Inter', 'Segoe UI', sans-serif"
                },
                padding: 20
            },
            tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                titleColor: '#F9FAFB',
                bodyColor: '#E5E7EB',
                borderColor: '#4B5563',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y;
                        } else if (context.parsed !== null) {
                            label += context.parsed;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#D1D5DB',  // 淡灰色
                    font: {
                        size: 11,
                        family: "'Inter', 'Segoe UI', sans-serif"
                    }
                },
                grid: {
                    color: 'rgba(75, 85, 99, 0.3)',  // 深色半透明網格
                    drawBorder: false
                }
            },
            y: {
                ticks: {
                    color: '#D1D5DB',
                    font: {
                        size: 11,
                        family: "'Inter', 'Segoe UI', sans-serif"
                    }
                },
                grid: {
                    color: 'rgba(75, 85, 99, 0.3)',
                    drawBorder: false
                }
            }
        }
    },

    // 升級配色方案 - 更鮮豔現代的漸變色
    colors: {
        threat: {
            CRITICAL: '#EF4444',  // 亮紅色
            HIGH: '#F97316',      // 亮橙色
            MEDIUM: '#FBBF24',    // 亮黃色
            LOW: '#34D399',       // 亮綠色
            INFO: '#94A3B8'       // 淡灰色
        },
        attacks: [
            '#3B82F6', // Blue - 保持
            '#A78BFA', // Purple - 更亮
            '#F472B6', // Pink - 更亮
            '#FBBF24', // Amber - 更亮
            '#34D399', // Green - 更亮
            '#818CF8', // Indigo - 更亮
            '#2DD4BF', // Teal - 更亮
            '#FB923C', // Orange - 更亮
            '#E879F9', // Fuchsia - 新增
            '#60A5FA', // Light Blue - 新增
        ],
        gradients: {
            blue: ['#3B82F6', '#1E40AF'],
            purple: ['#A78BFA', '#6D28D9'],
            pink: ['#F472B6', '#BE185D'],
            green: ['#34D399', '#047857'],
            orange: ['#FB923C', '#C2410C']
        }
    },

    // 銷毀現有圖表
    destroyChart(canvasId) {
        const existingChart = Chart.getChart(canvasId);
        if (existingChart) {
            existingChart.destroy();
        }
    },

    // 繪製圓餅圖 - 增強版
    renderPieChart(canvasId, data, title = '') {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        // 使用模運算循環分配顏色，確保每個標籤都有不同顏色
        const backgroundColors = labels.map((_, index) =>
            this.colors.attacks[index % this.colors.attacks.length]
        );

        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 3,
                    borderColor: '#1F2937',  // 深色邊框
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#FFFFFF',
                    hoverOffset: 8  // 懸停時外擴效果
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        ...this.defaultOptions.plugins.title,
                        display: !!title,
                        text: title
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    // 繪製甜甜圈圖 - 增強版
    renderDoughnutChart(canvasId, data, title = '') {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        // 智能配色：先嘗試威脅等級顏色，否則使用索引從 attacks 配色中選擇
        const backgroundColors = labels.map((label, index) =>
            this.colors.threat[label] || this.colors.attacks[index % this.colors.attacks.length]
        );

        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 3,
                    borderColor: '#1F2937',
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#FFFFFF',
                    hoverOffset: 12  // 懸停時外擴效果更明顯
                }]
            },
            options: {
                ...this.defaultOptions,
                cutout: '60%',  // 中空部分大小
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        ...this.defaultOptions.plugins.title,
                        display: !!title,
                        text: title
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    // 繪製柱狀圖 - 增強版（帶漸變色）
    renderBarChart(canvasId, data, title = '') {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        // 取前 10 名並排序
        const sortedData = Object.entries(data)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const labels = sortedData.map(([label]) => label);
        const values = sortedData.map(([, value]) => value);

        // 創建漸變色
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, '#3B82F6');
        gradient.addColorStop(1, '#1E3A8A');

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '攻擊次數',
                    data: values,
                    backgroundColor: gradient,
                    borderColor: '#60A5FA',
                    borderWidth: 0,
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: '#60A5FA',
                    hoverBorderColor: '#93C5FD',
                    hoverBorderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: false
                    },
                    title: {
                        ...this.defaultOptions.plugins.title,
                        display: !!title,
                        text: title
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            precision: 0
                        }
                    }
                }
            }
        });
    },

    // 繪製水平柱狀圖 - 增強版（多彩）
    renderHorizontalBarChart(canvasId, data, title = '') {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        // 排序並取前 10
        const sortedData = Object.entries(data)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const labels = sortedData.map(([label]) => label);
        const values = sortedData.map(([, value]) => value);

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '次數',
                    data: values,
                    backgroundColor: this.colors.attacks.slice(0, labels.length),
                    borderWidth: 0,
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: this.colors.attacks.slice(0, labels.length).map(color => color + 'CC'),
                    hoverBorderWidth: 2,
                    hoverBorderColor: '#FFFFFF'
                }]
            },
            options: {
                indexAxis: 'y', // 水平柱狀圖
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: false
                    },
                    title: {
                        ...this.defaultOptions.plugins.title,
                        display: !!title,
                        text: title
                    },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                // 水平柱状图数据在 x 轴，不是 y 轴
                                label += context.parsed.x;
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    x: {
                        ...this.defaultOptions.scales.x,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.x.ticks,
                            precision: 0
                        }
                    }
                }
            }
        });
    },

    // 繪製折線圖 - 增強版（帶漸變填充）
    renderLineChart(canvasId, data, title = '') {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        // 創建漸變填充
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
        gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.2)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '攻擊數量',
                    data: values,
                    borderColor: '#3B82F6',
                    backgroundColor: gradient,
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#3B82F6',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointHoverBackgroundColor: '#60A5FA',
                    pointHoverBorderColor: '#FFFFFF',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                ...this.defaultOptions,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        ...this.defaultOptions.plugins.title,
                        display: !!title,
                        text: title
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            precision: 0
                        }
                    }
                }
            }
        });
    },

    // 繪製世界地圖 - 地理分布熱力圖
    async renderWorldMap(canvasId, countriesData) {
        this.destroyChart(canvasId);

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        // 如果沒有數據，顯示提示
        if (!countriesData || countriesData.length === 0) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '16px Arial';
            ctx.fillStyle = '#666';
            ctx.textAlign = 'center';
            ctx.fillText('暫無地理位置數據', canvas.width / 2, canvas.height / 2);
            return;
        }

        try {
            // 加載地圖數據（TopoJSON 格式）
            const response = await fetch('https://unpkg.com/world-atlas@2.0.2/countries-50m.json');
            const worldData = await response.json();

            // 將國家數據轉換為 Chart.js Geo 需要的格式
            const features = ChartGeo.topojson.feature(worldData, worldData.objects.countries).features;

            // 創建國家名稱到代碼的映射（用於匹配）
            const countryNameMap = {
                'United States': 'US',
                'United States of America': 'US',
                'China': 'CN',
                'Russia': 'RU',
                'Russian Federation': 'RU',
                'Brazil': 'BR',
                'India': 'IN',
                'Germany': 'DE',
                'United Kingdom': 'GB',
                'France': 'FR',
                'Japan': 'JP',
                'South Korea': 'KR',
                'Korea, Republic of': 'KR',
                'Netherlands': 'NL',
                'Canada': 'CA',
                'Australia': 'AU',
                'Singapore': 'SG',
                'Ukraine': 'UA'
            };

            // 創建國家代碼到攻擊數據的映射
            const dataMap = {};
            countriesData.forEach(country => {
                dataMap[country.country_code] = country.attack_count;
            });

            console.log('Country data map:', dataMap);

            // 準備圖表數據 - 使用國家名稱匹配
            const chartData = features.map(feature => {
                const countryName = feature.properties.name;
                const countryCode = countryNameMap[countryName];
                const value = countryCode ? (dataMap[countryCode] || 0) : 0;

                return {
                    feature: feature,
                    value: value
                };
            });

            // 計算最大值用於顏色刻度
            const maxValue = Math.max(...Object.values(dataMap), 1);
            console.log('Max attack value:', maxValue);
            console.log('Countries with data:', Object.keys(dataMap).length);

            // 檢查匹配情況
            const matchedCountries = chartData.filter(d => d.value > 0);
            console.log('Matched countries on map:', matchedCountries.length);
            console.log('Sample matched data:', matchedCountries.slice(0, 3).map(d => ({
                name: d.feature.properties.name,
                id: d.feature.id,
                code: d.feature.properties.iso_a2,
                value: d.value
            })));
            console.log('First 5 feature IDs:', features.slice(0, 5).map(f => ({ id: f.id, name: f.properties.name })));

            // 創建顏色映射函數
            const getColorForValue = (value) => {
                if (value === 0) return 'rgba(200, 200, 200, 0.2)';

                const ratio = value / maxValue;
                if (ratio < 0.25) return `rgba(34, 197, 94, ${0.3 + ratio * 2})`;  // 綠色
                if (ratio < 0.5) return `rgba(234, 179, 8, ${0.4 + ratio})`;       // 黃色
                if (ratio < 0.75) return `rgba(249, 115, 22, ${0.5 + ratio})`;     // 橙色
                return `rgba(220, 38, 38, ${0.6 + ratio * 0.4})`;                   // 紅色
            };

            new Chart(canvas, {
                type: 'choropleth',
                data: {
                    labels: features.map(d => d.properties.name),
                    datasets: [{
                        label: '攻擊次數',
                        data: chartData,
                        backgroundColor: chartData.map(d => getColorForValue(d.value)),
                        borderColor: '#374151',
                        borderWidth: 0.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        title: {
                            display: false
                        },
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    return context[0].label;
                                },
                                label: function(context) {
                                    const value = context.raw.value;
                                    if (value === 0) return '攻擊次數: 0';

                                    // 查找對應的國家數據以顯示更多信息
                                    const countryCode = context.raw.feature.properties.iso_a2;
                                    const countryData = countriesData.find(c => c.country_code === countryCode);

                                    if (countryData) {
                                        return [
                                            `攻擊次數: ${countryData.attack_count}`,
                                            `高風險攻擊: ${countryData.high_risk_count}`,
                                            `平均風險分數: ${countryData.average_risk_score}`,
                                            `獨立 IP: ${countryData.unique_ip_count}`
                                        ];
                                    }
                                    return `攻擊次數: ${value}`;
                                }
                            }
                        }
                    },
                    scales: {
                        projection: {
                            axis: 'x',
                            projection: 'equalEarth'  // 使用等積地圖投影
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering world map:', error);
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '16px Arial';
            ctx.fillStyle = '#DC2626';
            ctx.textAlign = 'center';
            ctx.fillText('地圖加載失敗', canvas.width / 2, canvas.height / 2);
        }
    }
};
