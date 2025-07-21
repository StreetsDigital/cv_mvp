/**
 * Enhanced CV Analysis Frontend Integration - Part 2
 * Continuation of the frontend implementation
 */

            {
                title: 'Advanced Analytics',
                key: 'advanced_analytics',
                score: detailedAnalysis.advanced_analytics_score || 0,
                skills: enhancedSkills.advanced_analytics || []
            },
            {
                title: 'Affiliate Marketing',
                key: 'affiliate_marketing',
                score: detailedAnalysis.affiliate_marketing_score || 0,
                skills: enhancedSkills.affiliate_marketing || []
            },
            {
                title: 'Influencer Marketing',
                key: 'influencer_marketing',
                score: detailedAnalysis.influencer_marketing_score || 0,
                skills: enhancedSkills.influencer_marketing || []
            },
            {
                title: 'Platform Leadership',
                key: 'platform_leadership',
                score: detailedAnalysis.platform_leadership_score || 0,
                skills: enhancedSkills.platform_leadership || []
            },
            {
                title: 'Industry Expertise',
                key: 'industry_expertise',
                score: detailedAnalysis.industry_specialization_score || 0,
                skills: enhancedSkills.industry_expertise || []
            },
            {
                title: 'Remote Work Skills',
                key: 'remote_skills',
                score: detailedAnalysis.remote_capability_score || 0,
                skills: enhancedSkills.remote_skills || []
            },
            {
                title: 'Executive Capabilities',
                key: 'executive_skills',
                score: detailedAnalysis.executive_readiness_score || 0,
                skills: enhancedSkills.executive_skills || []
            },
            {
                title: 'Sales-Marketing Integration',
                key: 'sales_marketing',
                score: detailedAnalysis.sales_marketing_integration_score || 0,
                skills: enhancedSkills.sales_marketing || []
            }
        ];

        return categories.map(category => `
            <div class="skill-category-card">
                <div class="skill-category-header">
                    <span class="skill-category-title">${category.title}</span>
                    <span class="skill-category-score ${this.getScoreClass(category.score)}">
                        ${Math.round(category.score)}%
                    </span>
                </div>
                <div class="skills-content">
                    ${category.skills.length > 0 ? `
                        <ul class="skills-list">
                            ${category.skills.map(skill => `<li>${skill}</li>`).join('')}
                        </ul>
                    ` : `
                        <div class="no-skills-detected">No skills detected in this category</div>
                    `}
                </div>
            </div>
        `).join('');
    }

    getScoreClass(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        if (score >= 40) return 'score-average';
        return 'score-poor';
    }

    generateRecommendationsSection(result) {
        const recommendations = result.recommendations || [];
        const interviewQuestions = result.suggested_interview_questions || [];
        const strengths = result.strengths || [];
        const improvements = result.areas_for_improvement || [];

        return `
            <div class="recommendations-section" style="margin-top: 30px;">
                <h3>Analysis Insights & Recommendations</h3>
                
                ${strengths.length > 0 ? `
                    <div class="insights-card" style="margin: 15px 0; padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px;">
                        <h4 style="color: #155724; margin-top: 0;">✅ Key Strengths</h4>
                        <ul style="margin: 10px 0; color: #155724;">
                            ${strengths.map(strength => `<li>${strength}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${improvements.length > 0 ? `
                    <div class="insights-card" style="margin: 15px 0; padding: 20px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px;">
                        <h4 style="color: #856404; margin-top: 0;">⚡ Areas for Development</h4>
                        <ul style="margin: 10px 0; color: #856404;">
                            ${improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${recommendations.length > 0 ? `
                    <div class="insights-card" style="margin: 15px 0; padding: 20px; background: #cce5ff; border: 1px solid #99d6ff; border-radius: 8px;">
                        <h4 style="color: #004085; margin-top: 0;">💡 Hiring Recommendations</h4>
                        <ul style="margin: 10px 0; color: #004085;">
                            ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${interviewQuestions.length > 0 ? `
                    <div class="insights-card" style="margin: 15px 0; padding: 20px; background: #e2e3e5; border: 1px solid #d6d8db; border-radius: 8px;">
                        <h4 style="color: #383d41; margin-top: 0;">❓ Suggested Interview Questions</h4>
                        <ol style="margin: 10px 0; color: #383d41;">
                            ${interviewQuestions.map(question => `<li style="margin: 8px 0;">${question}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}
            </div>
        `;
    }

    displayStandardResults(result) {
        // Keep existing standard results display
        const resultsContainer = document.getElementById('results') || 
                               document.querySelector('.results-container');
        
        if (!resultsContainer) return;

        resultsContainer.innerHTML = `
            <div class="standard-summary">
                <h3>CV Analysis Results</h3>
                <p><strong>Candidate:</strong> ${result.candidate_name}</p>
                <p><strong>Overall Score:</strong> ${Math.round(result.overall_score)}%</p>
                <p><strong>Skills Match:</strong> ${Math.round(result.skills_match)}%</p>
                <p><strong>Experience Match:</strong> ${Math.round(result.experience_match)}%</p>
            </div>
        `;
    }

    displayError(message) {
        const resultsContainer = document.getElementById('results') || 
                               document.querySelector('.results-container');
        
        if (!resultsContainer) return;

        resultsContainer.innerHTML = `
            <div class="error-message" style="padding: 20px; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 8px;">
                <h4>Analysis Error</h4>
                <p>${message}</p>
                <p>Please try again or contact support if the issue persists.</p>
            </div>
        `;
    }

    // Enhanced export functionality
    exportResults(format = 'json') {
        const results = this.getLastAnalysisResults();
        if (!results) {
            alert('No analysis results to export');
            return;
        }

        switch (format) {
            case 'json':
                this.downloadJSON(results);
                break;
            case 'csv':
                this.downloadCSV(results);
                break;
            case 'pdf':
                this.generatePDF(results);
                break;
            default:
                console.error('Unsupported export format:', format);
        }
    }

    downloadJSON(data) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cv-analysis-${data.candidate_name || 'candidate'}-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    downloadCSV(data) {
        const csvData = this.convertToCSV(data);
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cv-analysis-${data.candidate_name || 'candidate'}-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        const headers = [
            'Candidate Name', 'Email', 'Overall Score', 'Skills Match', 'Experience Match',
            'SEO/SEM Score', 'MarTech Score', 'Advanced Analytics Score', 
            'Industry Specialization Score', 'Platform Leadership Score',
            'Remote Capability Score', 'Executive Readiness Score'
        ];

        const values = [
            data.candidate_name || '',
            data.candidate_email || '',
            Math.round(data.overall_score || 0),
            Math.round(data.skills_match || 0),
            Math.round(data.experience_match || 0),
            Math.round(data.detailed_analysis?.seo_sem_score || 0),
            Math.round(data.detailed_analysis?.martech_score || 0),
            Math.round(data.detailed_analysis?.advanced_analytics_score || 0),
            Math.round(data.detailed_analysis?.industry_specialization_score || 0),
            Math.round(data.detailed_analysis?.platform_leadership_score || 0),
            Math.round(data.detailed_analysis?.remote_capability_score || 0),
            Math.round(data.detailed_analysis?.executive_readiness_score || 0)
        ];

        return headers.join(',') + '\n' + values.join(',');
    }

    // Comparison functionality for multiple candidates
    addToComparison(analysisResult) {
        const comparisons = JSON.parse(localStorage.getItem('cv_comparisons') || '[]');
        comparisons.push({
            ...analysisResult,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('cv_comparisons', JSON.stringify(comparisons));
        this.updateComparisonUI();
    }

    updateComparisonUI() {
        const comparisons = JSON.parse(localStorage.getItem('cv_comparisons') || '[]');
        const comparisonContainer = document.getElementById('comparison-container');
        
        if (comparisonContainer && comparisons.length > 0) {
            comparisonContainer.innerHTML = `
                <div class="comparison-section" style="margin-top: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h4>Candidate Comparison (${comparisons.length} candidates)</h4>
                    <button onclick="cvAnalyzer.showComparisonView()" class="btn btn-secondary">
                        View Comparison
                    </button>
                    <button onclick="cvAnalyzer.clearComparisons()" class="btn btn-outline-danger" style="margin-left: 10px;">
                        Clear All
                    </button>
                </div>
            `;
        }
    }

    showComparisonView() {
        const comparisons = JSON.parse(localStorage.getItem('cv_comparisons') || '[]');
        if (comparisons.length === 0) return;

        // Create comparison table
        const comparisonHTML = this.generateComparisonTable(comparisons);
        
        // Show in modal or new section
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 1000; padding: 20px;
            overflow-y: auto;
        `;
        
        modal.innerHTML = `
            <div style="background: white; max-width: 1200px; margin: 0 auto; padding: 30px; border-radius: 12px;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 20px;">
                    <h3>Candidate Comparison</h3>
                    <button onclick="this.closest('.comparison-modal').remove()" 
                            style="background: #dc3545; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">
                        Close
                    </button>
                </div>
                ${comparisonHTML}
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    generateComparisonTable(comparisons) {
        const headers = ['Candidate', 'Overall Score', 'Skills Match', 'Experience', 'SEO/SEM', 'MarTech', 'Analytics', 'Industry', 'Leadership', 'Remote', 'Executive'];
        
        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-striped" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            ${headers.map(header => `<th style="padding: 12px; border: 1px solid #ddd;">${header}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${comparisons.map(candidate => `
                            <tr>
                                <td style="padding: 12px; border: 1px solid #ddd;">
                                    <strong>${candidate.candidate_name}</strong><br>
                                    <small>${candidate.candidate_email || ''}</small>
                                </td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">
                                    <span class="score-badge ${this.getScoreClass(candidate.overall_score)}" style="padding: 4px 8px; border-radius: 12px; color: white; font-weight: bold;">
                                        ${Math.round(candidate.overall_score || 0)}%
                                    </span>
                                </td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.skills_match || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.experience_match || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.seo_sem_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.martech_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.advanced_analytics_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.industry_specialization_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.platform_leadership_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.remote_capability_score || 0)}%</td>
                                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">${Math.round(candidate.detailed_analysis?.executive_readiness_score || 0)}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        return tableHTML;
    }

    clearComparisons() {
        if (confirm('Are you sure you want to clear all candidate comparisons?')) {
            localStorage.removeItem('cv_comparisons');
            this.updateComparisonUI();
        }
    }

    getLastAnalysisResults() {
        return this.lastAnalysisResults || null;
    }

    setLastAnalysisResults(results) {
        this.lastAnalysisResults = results;
    }
}

// Initialize enhanced CV analyzer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.cvAnalyzer = new EnhancedCVAnalyzer();
    
    // Update existing analyze button functionality
    const analyzeButton = document.getElementById('analyze-btn') || 
                         document.querySelector('.analyze-button');
    
    if (analyzeButton) {
        analyzeButton.addEventListener('click', async function() {
            const cvText = document.getElementById('cv-text')?.value || 
                          document.querySelector('.cv-input')?.value;
            const jobDescription = document.getElementById('job-description')?.value || 
                                 document.querySelector('.job-input')?.value;
            
            if (!cvText || !jobDescription) {
                alert('Please provide both CV text and job description');
                return;
            }
            
            // Show loading state
            this.disabled = true;
            this.textContent = 'Analyzing...';
            
            try {
                await window.cvAnalyzer.performAnalysis(cvText, jobDescription);
            } finally {
                this.disabled = false;
                window.cvAnalyzer.updateAnalysisButton();
            }
        });
    }
    
    // Add export buttons
    const resultsContainer = document.getElementById('results') || 
                           document.querySelector('.results-container');
    
    if (resultsContainer) {
        const exportButtonsHTML = `
            <div class="export-buttons" style="margin: 20px 0; text-align: center; display: none;">
                <button onclick="cvAnalyzer.exportResults('json')" class="btn btn-outline-primary">
                    Export JSON
                </button>
                <button onclick="cvAnalyzer.exportResults('csv')" class="btn btn-outline-success" style="margin-left: 10px;">
                    Export CSV
                </button>
                <button onclick="cvAnalyzer.addToComparison(cvAnalyzer.getLastAnalysisResults())" class="btn btn-outline-info" style="margin-left: 10px;">
                    Add to Comparison
                </button>
            </div>
            <div id="comparison-container"></div>
        `;
        
        resultsContainer.insertAdjacentHTML('afterend', exportButtonsHTML);
    }
});

// Override the original analysis function if it exists
if (typeof performAnalysis !== 'undefined') {
    console.log('Enhanced CV Analysis loaded - Standard analysis function overridden');
}
