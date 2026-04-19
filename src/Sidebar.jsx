
import { useState } from 'react'

function SideBar({setPage}) {

    return (
        <div>
            <button onClick={()=>{setPage("experience")}}>Experience</button>
            <button onClick={()=>{setPage("coverLetter")}}>Cover Letter</button>
        </div>
    );
}

export default SideBar;
