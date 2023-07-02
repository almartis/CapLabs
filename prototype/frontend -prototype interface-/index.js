const apiUrl = "http://192.168.0.128:8000";
const resources = ["/capsApi/process","/capsApi/slices"]

function loadSTL() {

    // Get the pack to use from the user
    let pack = select.value;
    let min = hu_min.value, max = hu_max.value, surflevel = level.value, seg_flag = segInp.checked ;

    slicers.axial.disabled = true;
    slicers.coronal.disabled = true;
    slicers.sagital.disabled = true;

    if(pack !== "")
    {
	// Create an object with the directory path
	const data = {
	    pack,
	    min,
	    max,
	    surflevel,
	    seg_flag,
	};
	// Send a POST request to the Python API
	fetch(apiUrl+resources[0], {
	    method: "POST",
	    headers: {
		"Content-Type": "application/json",
	    },
	    body: JSON.stringify(data),
	})
	    .then((response) => {
		if (response.ok !== true)
		{
		    throw new Error("Http Error:",`server responded with status code ${response.status}`);
		}
		
		return response.blob(); // Read all the response and send a promise that resolve with a blob object
	    })
	    .then((blob) => {
		// Create a URL object from the received blob
		stldata = blob;
		
		if(stldata !== "")
		{
		    slicers.axial.disabled = false;
		    slicers.coronal.disabled = false;
		    slicers.sagital.disabled = false;

		    if(gen3d.disabled === true)
		    {
			gen3d.disabled = false;
		    }
		}
	    })
	    .catch((error) => {
		console.error("Error:", error);
	    });
    }
}

function genURL()
{
    if(stldata !== "")
    {
	const urlLink = document.querySelector("#link");

	console.assert(urlLink !== undefined, "Error: Failed to create the 'a' html element");

	urlLink.innerHTML = "Link ready! Click to get the stl file.";

	if(prev_url != "")
	{
	    URL.revokeObjectURL(urlLink.href);
	}
	prev_url = URL.createObjectURL(stldata);
	urlLink.href = prev_url;

	gen3d.disabled = true;
    }
}

function check()
{
    if(segInp.checked === true)
    {
	hu_min.disabled = false;
	hu_max.disabled = false;
    }
    else
    {
	hu_min.disabled = true;
	hu_max.disabled = true;

	hu_min.value = "";
	hu_max.value = "";
    }
}

function getSlice()
{
}

let stldata = "";
let prev_url = "";

const select = document.querySelector("#dcmpack");
console.assert(select !== undefined,"Error: Failed to querySelect '#dcmpack'");

const segInp = document.querySelector("#seg_check");
console.assert(segInp !== undefined,"Error: Failed to querySelect '#seg_check'");

const hu_min = document.querySelector("#min_hu");
console.assert(hu_min !== undefined,"Error: Failed to querySelect '#min_hu'");

const hu_max = document.querySelector("#max_hu");
console.assert(hu_max !== undefined,"Error: Failed to querySelect '#max_hu'");

const level = document.querySelector("#level");
console.assert(hu_max !== undefined, "Error: Failed to querySelect '#level'");

const gen3d = document.querySelector("#gen3d");
console.assert(gen3d !== undefined, "Error: Failed to querySelect '#gen3d'");
gen3d.disabled = true;

const stl_url = document.querySelector("#stl_url");
console.assert(stl_url !== undefined, "Error: Failed to querySelect '#stl_url'");

const processdata = document.querySelector("#process");
console.assert(processdata !== undefined, "Error: Failed to querySelect '#process'");

const slicers = {
    'axial': document.querySelector("#axial_slicer"),
    'coronal': document.querySelector("#coronal_slicer"),
    'sagital': document.querySelector("#sagital_slicer"),
};

const slcval = {
    'axial': document.querySelector("#axVal"),
    'coronal': document.querySelector("#corVal"),
    'sagital': document.querySelector("#sagVal"),
};

slicers.axial.addEventListener("change", () => {
    slcval.axial.innerHTML = slicers.axial.value;

    const data = {
	'slice_type': "axial",
	'slice_nbr': slicers.axial.value,
    };
    
    // Send a POST request to the Python API
    fetch(apiUrl+resources[1], {
	method: "POST",
	headers: {
	    "Content-Type": "application/json",
	},
	body: JSON.stringify(data),
    })
	.then((response) => {

	    if (response.ok !== true)
	    {
		throw new Error("Http Error:",`server responded with status code ${response.status}`);
	    }
	    
	    return response.blob(); // Read all the response and send a promise that resolve with a blob object
	})
	.then((blob) => {
	    // Create a URL object from the received blob
	    let img = document.querySelector("#axial_view");

	    if(img.src != "")
	    {
		img.src = URL.createObjectURL(blob);
	    }
	    else
	    {
		URL.revokeObjectURL(img.src);
		img.src = URL.createObjectURL(blob);
	    }
	})
	.catch((error) => {
	    console.error("Error:", error);
	});
});

slicers.coronal.addEventListener("change", () => {
    slcval.coronal.innerHTML = slicers.coronal.value;

    const data = {
	'slice_type': "coronal",
	'slice_nbr': slicers.coronal.value,
    };
    
    // Send a POST request to the Python API
    fetch(apiUrl+resources[1], {
	method: "POST",
	headers: {
	    "Content-Type": "application/json",
	},
	body: JSON.stringify(data),
    })
	.then((response) => {

	    if (response.ok !== true)
	    {
		throw new Error("Http Error:",`server responded with status code ${response.status}`);
	    }
	    
	    return response.blob(); // Read all the response and send a promise that resolve with a blob object
	})
	.then((blob) => {
	    // Create a URL object from the received blob
	    let img = document.querySelector("#coronal_view");

	    if(img.src != "")
	    {
		img.src = URL.createObjectURL(blob);
	    }
	    else
	    {
		URL.revokeObjectURL(img.src);
		img.src = URL.createObjectURL(blob);
	    }
	})
	.catch((error) => {
	    console.error("Error:", error);
	});
});

slicers.sagital.addEventListener("change", () => {
    slcval.sagital.innerHTML = slicers.sagital.value;
    
    const data = {
	'slice_type': "sagital",
	'slice_nbr': slicers.sagital.value,
    };

    // Send a POST request to the Python API
    fetch(apiUrl+resources[1], {
	method: "POST",
	headers: {
	    "Content-Type": "application/json",
	},
	body: JSON.stringify(data),
    })
	.then((response) => {

	    if (response.ok !== true)
	    {
		throw new Error("Http Error:",`server responded with status code ${response.status}`);
	    }
	    
	    return response.blob(); // Read all the response and send a promise that resolve with a blob object
	})
	.then((blob) => {
	    // Create a URL object from the received blob
	    let img = document.querySelector("#sagital_view");

	    if(img.src != "")
	    {
		img.src = URL.createObjectURL(blob);
	    }
	    else
	    {
		URL.revokeObjectURL(img.src);
		img.src = URL.createObjectURL(blob);
	    }
	})
	.catch((error) => {
	    console.error("Error:", error);
	});
});

slicers.axial.disabled = true;
slicers.coronal.disabled = true;
slicers.sagital.disabled = true;

segInp.addEventListener("click",check);
gen3d.addEventListener("click",genURL);
process.addEventListener("click",loadSTL);

check();
