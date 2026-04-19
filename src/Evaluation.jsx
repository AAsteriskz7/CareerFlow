
import { useState } from 'react'

function Evaluation({evaluation}) {

    

    return (
        <div>
            {/* {{
                'score': <integer from 0 to 10>,
                'score_justification': '<short explanation of the score>',
                'strengths': ['<list key strengths or perfectly aligned experiences>'],
                'missing_skills': ['<list skills or experiences not covered>'],
                'questions': ['<list questions to gather additional user input>']
            }} */}

            <h2>Evaluation</h2>
            <h3>Score: {evaluation?.score}</h3>
            <h3>Overview:</h3>
            <h4>{evaluation?.score_justification}</h4>
            <h3>Strengths</h3>
            {evaluation?.strengths?.map((strength, index) => {
                return(
                    <p key={index}>{strength}</p>
                )
            })}
            <h3>Missing Skills</h3>
            {evaluation?.missing_skills?.map((missingSkill, index) => {
                return(
                    <p key={index}>{missingSkill}</p>
                )
            })}
            <h3>Questions</h3>
            {evaluation?.questions?.map((question, index) => {
                return(
                    <p key={index}>{question}</p>
                )
            })}
        </div>
    );
}

export default Evaluation;
