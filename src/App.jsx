import { useState, useEffect } from 'react'
import './App.css'
import Experiences from './Experiences'
import Evaluation from './Evaluation'
import SideBar from './Sidebar'

function App() {
//   const [jobDesc, setJobDesc] = useState(`Job Title: Web Security Expert
// Location: Austin, TX (Hybrid)
// Company: NexaTech Solutions

// About the Company

// NexaTech Solutions is a fast-growing technology firm specializing in cloud services, enterprise software, and cybersecurity solutions. We help organizations safeguard their digital infrastructure while enabling scalable, secure innovation.

// Job Summary

// We are seeking a highly skilled Web Security Expert to protect our web applications, systems, and networks from evolving cyber threats. The ideal candidate will have deep expertise in identifying vulnerabilities, implementing security measures, and responding to incidents across a variety of web technologies.

// Key Responsibilities
// Conduct regular security assessments, vulnerability scans, and penetration testing of web applications
// Identify, analyze, and remediate security risks and threats
// Develop and implement secure coding practices and standards
// Monitor systems for suspicious activity and respond to security incidents
// Collaborate with development teams to ensure security is integrated throughout the software lifecycle
// Manage firewalls, intrusion detection/prevention systems, and web application firewalls (WAF)
// Stay up to date with the latest security trends, threats, and technologies
// Prepare detailed reports on findings, risks, and mitigation strategies
// Ensure compliance with industry standards and regulations (e.g., OWASP, ISO 27001, GDPR)
// Required Qualifications
// Bachelor’s degree in Computer Science, Cybersecurity, or related field (or equivalent experience)
// 3+ years of experience in web security or cybersecurity roles
// Strong understanding of web application vulnerabilities (e.g., XSS, SQL injection, CSRF)
// Experience with security tools such as Burp Suite, Nessus, or Metasploit
// Knowledge of network protocols, encryption, and authentication mechanisms
// Familiarity with secure coding practices in languages like JavaScript, Python, or Java
// Preferred Qualifications
// Certifications such as CEH, CISSP, or OSCP
// Experience with cloud security (AWS, Azure, or GCP)
// Knowledge of DevSecOps practices and CI/CD pipeline security
// Familiarity with container security (Docker, Kubernetes)
// Key Skills
// Analytical and problem-solving skills
// Attention to detail
// Strong communication and teamwork abilities
// Ability to work under pressure and manage multiple priorities
// Benefits
// Competitive salary and performance bonuses
// Health, dental, and vision insurance
// Flexible work arrangements
// Professional development and certification support
// Generous paid time off
// How to Apply

// Interested candidates should submit their resume and a brief cover letter outlining their experience in web security and recent projects.
// `)
  const [jobDesc, setJobDesc] = useState(() => {
    return localStorage.getItem("jobDesc") || ""
  })
  const [coverLetter, setCoverLetter] = useState(() => {
    return localStorage.getItem("coverLetter") || ""
  })
  // const [experiences, setExperiences] = useState([
  //     {
  //           "role": "Cybersecurity Intern",
  //           "company": "SecureTech Solutions",
  //           "highlights": [
  //               "Assisted in monitoring network traffic for suspicious activity using basic SIEM tools, identifying 50+ potential threats per week",
  //               "Conducted vulnerability scans and documented findings for senior analysts, resulting in remediation of 30+ high-risk vulnerabilities",
  //               "Helped implement security best practices such as password policies and MFA, increasing compliance by 25%"
  //           ]
  //       },
  //       {
  //           "role": "IT Support Technician (Part-Time)",
  //           "company": "NextGen IT Services",
  //           "highlights": [
  //               "Troubleshot hardware, software, and network issues for 20+ small business clients monthly",
  //               "Configured firewalls and antivirus software to improve endpoint security, reducing incidents by 40%",
  //               "Educated users on phishing risks and safe browsing habits, resulting in a 35% decrease in successful phishing attempts"
  //           ]
  //       },
  //       {
  //           "role": "Cybersecurity Lab Project",
  //           "company": "Personal Project",
  //           "highlights": [
  //               "Built a home lab using virtual machines to simulate 10+ network attack scenarios",
  //               "Practiced penetration testing techniques using tools like Nmap and Wireshark, identifying 15+ vulnerabilities in simulated environments",
  //               "Documented attack scenarios and mitigation strategies, creating a 25-page reference guide"
  //           ]
  //       },
  //       {
  //           "role": "Web Security Assistant",
  //           "company": "BlueWave Digital",
  //           "highlights": [
  //               "Reviewed website code for basic security vulnerabilities such as XSS and SQL injection, fixing 12 critical issues",
  //               "Assisted in implementing HTTPS and secure authentication methods across 5 client websites",
  //               "Collaborated with developers to improve secure coding practices, increasing secure code adherence by 30%"
  //           ]
  //       },
  //       {
  //           "role": "Capture The Flag (CTF) Participant",
  //           "company": "University Cyber Club",
  //           "highlights": [
  //               "Participated in cybersecurity competitions focused on cryptography, forensics, and web exploits, ranking in the top 15% in 3 events",
  //               "Solved 20+ challenges involving password cracking and reverse engineering",
  //               "Worked in a team to analyze and exploit simulated vulnerabilities, achieving 90% challenge completion rate"
  //           ]
  //       }
  // ])
  const [experiences, setExperiences] = useState(() => {
    const stored = localStorage.getItem("experiences")
    return stored ? JSON.parse(stored) : []
  })
  const [notes, setNotes] = useState(() => {
    return localStorage.getItem("notes") || ""
  })
  const [evaluation, setEvaluation] = useState(() => {
    const stored = localStorage.getItem("evaluation")
    return stored ? JSON.parse(stored) : {}
  })
  const [isLoading, setIsLoading] = useState(false)

  const [page, setPage] = useState("experience")

  useEffect(() => {
    localStorage.setItem("jobDesc", jobDesc)
  }, [jobDesc])
  useEffect(() => {
    localStorage.setItem("coverLetter", coverLetter)
  }, [coverLetter])
  useEffect(() => {
    localStorage.setItem("notes", notes)
  }, [notes])
  useEffect(() => {
    localStorage.setItem("evaluation", JSON.stringify(evaluation))
  }, [evaluation])  
  useEffect(() => {
    localStorage.setItem("experiences", JSON.stringify(experiences))
  }, [experiences])

  async function generateCoverLetter() {
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/generate_cover_letter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            experience: experiences,
            job_description: jobDesc
        }),
      })

      if(response.ok) {
        const data = await response.json()
        console.log(data)
        setCoverLetter(data.cover_letter)
        setNotes("")
        evaluateCoverLetter(data.cover_letter)
      } else {
        console.log("Error retrieving from generate_cover_letter")
      }
    } catch (e) {
      console.log("Error calling generate_cover_letter: ", e)
    }

    setIsLoading(false)
  }

  async function modifyCoverLetter() {
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/modify_cover_letter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            experience: experiences,
            job_description: jobDesc,
            draft_cover_letter: coverLetter,
            evaluation: evaluation,
            user_notes: notes
        }),
      })

      if(response.ok) {
        const data = await response.json()
        console.log(data)
        setCoverLetter(data.cover_letter)
        evaluateCoverLetter(data.cover_letter)
      } else {
        console.log("Error retrieving from modify_cover_letter")
      }
    } catch (e) {
      console.log("Error calling modify_cover_letter: ", e)
    }

    setIsLoading(false)
  }

  async function evaluateCoverLetter(coverLetterNew) {
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/evaluate_cover_letter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            experience: experiences,
            job_description: jobDesc,
            draft_cover_letter: coverLetterNew,
        }),
      })

      if(response.ok) {
        const data = await response.json()
        console.log(data)
        setEvaluation(data.evaluation)
        setNotes("")
      } else {
        console.log("Error retrieving from evaluate_cover_letter")
      }
    } catch (e) {
      console.log("Error calling evaluate_cover_letter: ", e)
    }

    setIsLoading(false)
  }

  

  return (
    <>
      <div>

        {isLoading && <h1>Loading...</h1>}
        <SideBar setPage={setPage}></SideBar>

        {page == "experience" && 
          <Experiences experiences={experiences} setExperiences={setExperiences}></Experiences>
        }

        {page == "coverLetter" &&
          <div>
            <div id="jobDescription">
              <h2>Job Description: </h2>
              <textarea value={jobDesc} onChange={(e) => {setJobDesc(e.target.value)}} disabled={isLoading}></textarea>
            </div>
            <div id="coverLetter">
              <h2>Cover Letter: </h2>
              <textarea value={coverLetter} onChange={(e) => {setCoverLetter(e.target.value)} } disabled={isLoading}></textarea>
            </div>
            {coverLetter.length > 0 && 
              <div id="notes">
                <h2>Notes:</h2>
                <h3>(Any specific notes to modify the cover letter)</h3>
                <textarea value={notes} onChange={(e) => {setNotes(e.target.value)} } disabled={isLoading}></textarea>
              </div>
            }


            {coverLetter.length > 0 ?
              <button id="modifyCoverLetter" onClick={modifyCoverLetter} disabled={isLoading}>Modify Cover Letter</button>
              : <button id="generateCoverLetter" onClick={generateCoverLetter} disabled={isLoading}>Generate Cover Letter</button>
            }

            <Evaluation evaluation={evaluation}></Evaluation>

            <button onClick={()=>{evaluateCoverLetter(coverLetter)}} disabled={isLoading}>Evaluate</button>
          </div>
        }
      </div>
    </>
  )
}

export default App
