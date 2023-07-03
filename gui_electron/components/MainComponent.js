import { useState, useEffect } from 'react';

// styles
const graph_iframe_style = {
    width: "75vw",
    height: "75vh"
};

const sidebar_style = {
    width: "20vw",
    height: "100vh",
    float: "left",
    background: "#ECEEEF",
    margin: "0px"
};

const sidebar_list = {
    overflow: "scroll",
    height: "92%"
}

const sidebar_content_notCurrent = { // 선택되지 않은 일반 리스트
    width: "100%",
    padding: "5px",
    margin: "5px"

}

const sidebar_content_current = { // 선택이 된 리스트 항목
    width: "100%",
    borderBottom: "solid 2px #7dbae5",
    padding: "5px",
    margin: "5px"
};


const tab_menu_style = {
    width: "75vw",
    height: "10vh",
    background: "blue",
    margin: "0px"
};

const current_tab = {
    margin: "0px"
};

const not_current_tab = {
    width: "75vw",
    height: "100vh",
    float: "right",
    display: "none",
}

const tab_container = {
    width: "75vw",
    height: "89vh",
    float: "right",
    margin: "0px"
}

//

function showGraph(terminal) {
    let tmp = document.querySelector('#graph-iframe');
    console.log(terminal);
    tmp.src = `${terminal}`;
}


function MainComponent(props) {
    const [ spectrumIdx, setSpectrumIdx ] = useState(0); 

    const [NisPushed, setNPushed] = useState(false);
    const [CisPushed, setCPushed] = useState(false);

    const [graphUrl, setGraphUrl] = useState(false);

    const [tabIdx, setTabIdx] = useState(0);
    let terminal;

    useEffect(()=>{
        checkStates();
    }, [NisPushed, CisPushed, spectrumIdx]);

    function checkStates() {
        let terminal;
        if(NisPushed === true && CisPushed === true) {
            terminal = './spectrums/spectrum_ncterm'+spectrumIdx+'.html';
        } else if(NisPushed === true && CisPushed == false) { // N만 눌린 상태
            terminal = './spectrums/spectrum_nterm'+spectrumIdx+'.html';
        } else if(CisPushed === true && NisPushed === false) {
            terminal = './spectrums/spectrum_cterm'+spectrumIdx+'.html';
        } else if(CisPushed === false && NisPushed === false){
            terminal = './spectrums/spectrum_naive'+spectrumIdx+'.html';
        }

        // showGraph(terminal);
        setGraphUrl(terminal);
    } 
    
    function toggleNBtn() {
        setNPushed(!NisPushed);

    }

    function toggleCBtn() {
        setCPushed(!CisPushed);
    }


    function reShowGraph(idx, title, seq, terminal) {

        
        if(spectrumIdx === idx) return;
    
        setSpectrumIdx(idx);
    
        setGraphUrl(terminal)
    }
    
    
    const spectrum_list = props.data.map((obj) => 
            <div key={obj.title}
            onClick={() => reShowGraph(obj.idx, obj.title, obj.seq)}
            style={spectrumIdx===obj.idx ? sidebar_content_current: sidebar_content_notCurrent}>{obj.title}</div>
    );
    return (
        <div>
        <div id="sidebar" style={sidebar_style}>
            <h3>Spectrums</h3>
            <div style={sidebar_list}>
                {spectrum_list}
            </div>
        </div>
        <div id="tab-container" style={tab_container}>
        <div id="tab_menu" style={tab_menu_style}>
            <button onClick={()=>{setTabIdx(1)}}>hihi</button>
            <button onClick={()=>{setTabIdx(0)}}>bye</button>
        </div>

        <div id='content_0' style={tabIdx === 0? current_tab : not_current_tab}>
            <div id="spectrum-info">
                <h3>{data[spectrumIdx].title}</h3>
                <h4>{data[spectrumIdx].seq}</h4>
            </div>
            <div id='term-btns'>
                <button id='n-btn' onClick={toggleNBtn}>N</button>
                <button id='c-btn' onClick={toggleCBtn}>C</button>
            </div>
            <iframe style={graph_iframe_style} src={graphUrl}></iframe>
        </div>

        <div id='content_1' style={tabIdx === 1? current_tab : not_current_tab}>
            <p>💙준비중인 페이지입니다.</p>

        </div>
        </div>
    </div>
    )
}