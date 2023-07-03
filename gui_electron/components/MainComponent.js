import { useState, useEffect } from 'react';

// begin styles
const graph_iframe_style = {
    width: "75vw",
    height: "75vh",
    border: "0px",
};

const sidebar_style = {
    width: "18vw",
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

const sidebar_content_current = { // 선택이 된 리스트 항목 (파란 밑줄)
    width: "25vw",
    borderBottom: "solid 2px #7dbae5",
    padding: "5px",
    margin: "5px",
};


const tab_menu_style = { // 탭 메뉴 전체를 감싸고 있는 탭
    width: "75vw",
    height: "7vh",
    margin: "0px",
    background: "#374047",
    display: "flex"
};

const current_tab = { // 선택된 탭
    margin: "0px"
};

const not_current_tab = { // 선택되지 않은 탭
    width: "75vw",
    height: "100vh",
    float: "right",
    display: "none",
}

const tab_container = { // tab menu와 tab content 전체를 감싸고 있는 요소
    width: "78vw",
    height: "89vh",
    float: "right",
    margin: "0px"
}

const tab_menu_component = {
    padding: "10px",
    background: "#374047",
    color: "white",
    float: "bottom",

};

const tab_menu_component_current = {
    padding: "10px",
    background: "white",
    color: "black",
    borderBottom: "solid 10px white",
    borderTop: "solid 2px #374047",
    margin: "0px"

};

const Nbtn = {
    width: "30px",
    height: "30px",
    border: "solid 3px #2d8fd5",
    background: "white",
    margin: "5px"
};

const Nbtn_pushed = {
    width: "30px",
    height: "30px",
    background: "#004170",
    margin: "5px"
};


const Cbtn = {
    width: "30px",
    height: "30px",
    border: "solid 3px #e6838b",
    background: "white",
    margin: "5px"
};

const Cbtn_pushed = {
    width: "30px",
    height: "30px",
    background: "#85000b",
    margin: "5px"
}

// end styles

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
                {tabIdx === 0? spectrum_list : "준비중입니다."}
            </div>
        </div>
        <div id="tab-container" style={tab_container}>
            <div id="tab_menu" style={tab_menu_style}>
                <div style={tabIdx===0? tab_menu_component_current : tab_menu_component} onClick={()=>{setTabIdx(0)}}>View Spectrums</div>
                <div style={tabIdx===1? tab_menu_component_current : tab_menu_component} onClick={()=>{setTabIdx(1)}}>Library matching</div>
            </div>

            <div id='content_0' style={tabIdx === 0? current_tab : not_current_tab}>
                <div id="spectrum-info">
                    <h3>Title: {data[spectrumIdx].title}</h3>
                    <h4>Seq: {data[spectrumIdx].seq}</h4>
                </div>
                <div id='term-btns'>
                    <button id='n-btn' onClick={toggleNBtn} style={NisPushed? Nbtn_pushed : Nbtn}>N</button>
                    <button id='c-btn' onClick={toggleCBtn} style={CisPushed? Cbtn_pushed : Cbtn}>C</button>
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