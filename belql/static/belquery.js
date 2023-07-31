
function query_bel(){
    $('#loading-bel').show();

    $.ajax({
        url: "/",
        type: "POST",
        data: {
            'q_sub': $("#bel-subject-query").val(),
            'q_rel': $("#bel-relation-query").val(),
            'q_obj': $("#bel-object-query").val()
        },
        dataType: 'json',

        success: function(response) {
                //create_bel_table(response.tab_options);
                create_table('result', 'bel-table');
                fill_table('bel-table', response);
                $('#loading-bel').hide();
            },

        error: function(xhr,errmsg,err){
            alert("Error! Check your console for further information.");
            console.log('Values:\n(q_sub): '+$("#bel-subject-query").val()+'\n(q_rel): '+$("#bel-relation-query").val()+'\n(q_obj): '+$("#bel-object-query").val());
            $('#loading-bel').hide();
        },
    });

}

function create_table(container_div, table_id){
    var result_div = document.getElementById(container_div);
    result_div.innerHTML='';

    var content_table = document.createElement('table');
    content_table.setAttribute('id', table_id);
    content_table.setAttribute('class', "table table-condensed table-bordered");
    content_table.setAttribute('style', "table-layout:fixed; width:inherit;");

    var content_table_head = document.createElement('thead');
    content_table_head.setAttribute('id', table_id+'-head');

    var content_table_body = document.createElement('tbody');
    content_table_body.setAttribute("id", table_id+"-body");

    content_table.appendChild(content_table_head);
    content_table.appendChild(content_table_body);
    result_div.appendChild(content_table);
}

function fill_table(table_id, table_data, data_tables=true){

    var tablehead = document.getElementById(table_id+'-head');
    var column_row = tablehead.insertRow(-1);

    var data_present = true;

    // Setup Column headers
    for (column_name_pos in table_data.column_names){
        var new_heading = document.createElement('th');
        new_heading.innerHTML = table_data.column_names[column_name_pos];
        column_row.appendChild(new_heading);
    };

    var tablebody = document.getElementById(table_id+'-body');
    if(table_data.data_rows.length > 0){
        for (row in table_data.data_rows){
            var newDataRow = tablebody.insertRow(-1);
            for (cell in table_data.data_rows[row]){

                if(table_data.ref_list.includes(parseInt(cell))){
                    var cell_data = create_link(table_data.ref_links[cell]+table_data.data_rows[row][cell], table_data.data_rows[row][cell]);
                }else{
                    var cell_data = document.createTextNode(table_data.data_rows[row][cell]);
                }
                // Insert cell content
                newDataRow.insertCell(cell).appendChild(cell_data);
            };
        };
    }else{
        var defaultDataRow = tablebody.insertRow(-1);
        var defaultCell = defaultDataRow.insertCell(0);
        defaultCell.innerHTML = "<b>No data found in graph</b>";
        defaultCell.colSpan = table_data.column_names.length;
        defaultCell.style = "text-align: center;";
        data_present = false;
    };

    // Activate Datatables
    if(data_tables && data_present){
        $('#'+table_id).DataTable();
    };

}

function create_link(href, txt){
    var new_link = document.createElement('a');
    new_link.setAttribute('href', href);
    new_link.setAttribute('target','_blank');
    new_link.innerHTML = txt;
    return new_link;
}

// BEL Path viz.js functionality
$("#gobtn").click(function(e) {
    $('#loading-bel').show();

    if(document.contains(document.getElementById('bel-svg'))){
        document.getElementById('bel-svg').remove();
    };

    document.getElementById('result-tables').innerHTML="";
    document.getElementById('bel-tables').innerHTML="";
    document.getElementById('experiment-tables').innerHTML="";
    document.getElementById("svg-node-list").innerHTML="";
    document.getElementById('graph-experiment-tables').innerHTML="";

    let activeTab_id = $(".querytab.tab-pane.active").attr('id');
    let query_var = {};
    let graph_engine = "dot";
    switch(activeTab_id){
        case 'pathquery':
            query_var = {
                'qtype': 'pathquery',
                'pfrom': $("#pfrom").val(),
                'pto': $("#pto").val(),
                'depth': $('#pdepth_min').val() + '-' + $('#pdepth_max').val(),
            };
            break;
        case 'pubquery':
            query_var = {
                'qtype': 'pubquery',
                'pmid': $("#pubPmid").val(),
                'laname': $("#pubLauth").val(),
                'pub_title': $("#pubTitle").val(),
                'pub_journal': $("#pubJournal").val(),
                'larelation': $("#pubRel").val(),
                'pub_year': $("#pubYear").val(),
                'pub_anno': $("#pubAnno").val()
            };
            break;
        case 'lastauthorquery':
            query_var = {
                'qtype': 'lastauthorquery',
                'laname': $("#authorname").val(),
                'larelation': $('#larelation').val(),
                'laentity': $('#bioentity').val()
            };
            break;
        case 'subgraphquery':
            query_var = {
                'qtype': 'subgraphquery',
                'subgraph': $("#sgChoose").val(),
                'sgpubPmid': $('#sgpubPmid').val(),
                'sgrelation': $('#sgrelation').val(),
            };
            break;
        case 'difquery':
            query_var = {
                'qtype': 'difquery',
                'difEndpoint': $("#difEndpoint").val(),
                'difPmod': $('#difPmod').val(),
                'difIntAction': $('#difIntAction').val(),
                'difDruggable': $('#difDruggable').val(),
                'difDrugAction': $('#difDrugAction').val(),
            };
            graph_engine = "circo";
            break;
    }

    $.ajax({
        url: "/ajax/belpath/",
        type: "POST",
        data: query_var,
        dataType: 'json',

        success: function(response) {
            $('#loading-bel').hide();
            $('#building-svg').show();
            var graph = response.dot_def;
            var options = {
                format: 'fdp',
                engine: graph_engine,
            };

            let viz = new Viz();
            viz.renderSVGElement(graph, options).then(function(element) {
                document.getElementById('result-svg').appendChild(element);
                element.setAttribute('id', 'bel-svg');

                // Add PanZoom functionality
                svgPanZoom(element, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true,
                    minZoom: 0.5,
                    maxZoom: 100,
                });

                // Add Click events
                //var allNodes = $("g.node");
                var allEdges = $("g.edge");

                allEdges.on("click", function() {
                  $('.selected').removeClass('selected');
                  $(this).addClass('selected');
                  edge_info(this.id);
                });

            });

            var select_field = document.getElementById("svg-node-list");
            for(element in response.node_map){
               var opt = document.createElement("option");
               opt.value = response.node_map[element][1];
               opt.innerHTML = response.node_map[element][0]; // whatever property it has

               // then append it to the select element
               select_field.appendChild(opt);
            }

            select_field.ondblclick = function(){highlight();};

            create_table('graph-experiment-tables', 'gexpt');
            fill_table('gexpt', response.experiment_highlighting);

            $('#building-svg').hide();

        },
        error: function(xhr,errmsg,err){
            alert("Error! Check your console for further information.");
            console.log("Internal URL:\n/ajax/belpath/\n\nValues:\n"+query_var);
        }
    });
});

$("#apply-location-filter").click(function(e){
    highlight();
});

function highlight(){
    $('#loading-bel').show();

    let allNodes = $("g.node");

    let itemList = document.getElementById("svg-node-list");
    let collection = itemList.selectedOptions;

    let highlight_nodes = [];
    for(i=0; i < collection.length; i++){
        highlight_nodes = highlight_nodes.concat(collection[i].value.split(','));
    };

    for(i=0; i < allNodes.length; i++){
        if(highlight_nodes.length > 0){
            allNodes[i].children[1].children[0].children[0].setAttribute('style','fill:lightgrey;');
            if(highlight_nodes.includes(allNodes[i].id)){
                allNodes[i].children[1].children[0].children[0].setAttribute('style','stroke-width:4px;stroke:red;');
            };
        } else {
            allNodes[i].children[1].children[0].children[0].removeAttribute('style');
        }

    };

    $('#loading-bel').hide();
}

function edge_info(target_rid){

    //$('#loading-bel').show();
    $.ajax({
        url: "/ajax/bel_info/edge/",
        type: "POST",
        data: {
            'rid': target_rid
        },
        dataType: 'json',

        success: function(response) {
                create_table('bel-tables', 'bel-statements');
                fill_table('bel-statements', response.statement_dict, false);

                create_table('experiment-tables', 'experiment-details');
                fill_table('experiment-details', response.experiment_dict, false);

                create_table('result-tables', 'bel-details');
                fill_table('bel-details', response.update_dict, false);
                //$('#loading-bel').hide();
            },

        error: function(xhr,errmsg,err){
            alert("Error! Check your console for further information.");
            console.log("Internal URL:\n/ajax/bel_info/edge/\n\nValues:\nrid: "+target_rid);
        },
    });

}

function split_strip(array_string){
    var array = array_string.split(',').map(function(item) {
      return item.trim();
    });
    return array;
}
