
function query_bel(){
    let loadGif = document.getElementById('loading-bel');
    loadGif.style.visibility = "visible";
    // $('#loading-bel').show();

    $.ajax({
        url: "/",
        type: "POST",
        data: {
            'q_sub': $("#bel-subject-query").val(),
            'q_rel': $("#bel-relation-query").val(),
            'q_obj': $("#bel-object-query").val(),
            'q_anno_key': $("#bel-anno-key-query").val(),
            'q_anno_val': $("#bel-anno-val-query").val(),
        },
        dataType: 'json',

        success: function(response) {
                //create_bel_table(response.tab_options);
                loadGif.style.visibility = "hidden";
                create_table('result', 'bel-table');
                fill_table('bel-table', response);
                // $('#loading-bel').hide();
            },

        error: function(xhr,errmsg,err){
            alert("Error! Check your console for further information.");
            console.log(
                'Values:\n(q_sub): ' + $("#bel-subject-query").val() +
                '\n(q_rel): ' + $("#bel-relation-query").val() +
                '\n(q_obj): '+$("#bel-object-query").val() +
                '\n(q_anno_key): '+$("#bel-anno-key-query").val() +
                '\n(q_anno_val): '+$("#bel-anno-val-query").val()
            );
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
    } else{
        var defaultDataRow = tablebody.insertRow(-1);
        var defaultCell = defaultDataRow.insertCell(0);
        defaultCell.innerHTML = "<b>No data found in graph</b>";
        defaultCell.colSpan = table_data.column_names.length;
        defaultCell.style = "text-align: center;";
        data_present = false;
    };

    // Activate Datatables
    if(data_tables && data_present){
        $('#'+table_id).DataTable({
            dom: 'lfBrtip',
            searching: false,
            buttons: [
                {
                    extend: 'csv',
                    filename: 'belql'
                },
            ]
        });
    }

}

function create_link(href, txt){
    var new_link = document.createElement('a');
    new_link.setAttribute('href', href);
    new_link.setAttribute('target','_blank');
    new_link.innerHTML = txt;
    return new_link;
}

function populateAnnoVals(){
    let annoDiv = document.getElementById("bel-anno-val-query")
    $.ajax({
        url: "/anno",
        type: "POST",
        data: {
            'anno_key': $("#bel-anno-key-query").val()
        },
        dataType: 'json',
        success: function(response) {
            for (const annoVal of response.anno_vals){
                let newOption = document.createElement('option');
                newOption.setAttribute("value", annoVal);
                newOption.innerHTML = annoVal;
                newOption.value = annoVal;
                annoDiv.options.add(newOption);
            }
        },
        error: function(xhr) {
           //Do Something to handle error
        }
    });
}

