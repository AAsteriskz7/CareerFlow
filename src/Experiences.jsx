
import { useState } from 'react'

function Experiences({experiences, setExperiences}) {

    return (
        <div>
            <h2>Experience: </h2>
            {experiences.map((experience, experienceIndex) => {
                return (
                    <div key={experienceIndex}>
                        <h3>Title</h3>
                        <input value={experience.company} onChange={(e) => {
                            const newExperiences = [...experiences];
                            newExperiences[experienceIndex].company = e.target.value;
                            setExperiences(newExperiences);
                        }}></input>
                        <h3>Role</h3>
                        <input value={experience.role} onChange={(e) => {
                            const newExperiences = [...experiences];
                            newExperiences[experienceIndex].role = e.target.value;
                            setExperiences(newExperiences);
                        }}></input>
                        <h3>Highlights</h3>
                        {experience.highlights.map((highlight, highlightIndex) => {
                            return (
                                <div key={highlightIndex}>
                                    <input value={highlight} onChange={(e) => {
                                        const newHighlights = [...experience.highlights];
                                        newHighlights[highlightIndex] = e.target.value;

                                        const newExperiences = [...experiences];
                                        newExperiences[experienceIndex].highlights = newHighlights;
                                        setExperiences(newExperiences);
                                    }}></input>
                                </div>
                            )
                        })}
                        <button onClick={() => {
                            const newHighlights = [...experience.highlights, ""]

                            const newExperiences = [...experiences];
                            newExperiences[experienceIndex].highlights = newHighlights;
                            setExperiences(newExperiences);
                        }}>+</button>
                    </div>
                )
            })}

            <button onClick={()=> {
                const newExperiences = [...experiences,
                    {
                        title: "",
                        role: "",
                        highlights: []
                    }
                ]
                setExperiences(newExperiences);
            }}>Add experience</button>

        </div>
    );
}

export default Experiences;
