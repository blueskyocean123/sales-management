
const search = {
    data(){
        return{
            searchedData: false,
            showTable: true,
            showPagination: true,
            noData: false,
            data: [],
            url: ''
        }
    },
    methods: {
        // search sells
        searchSellProdyct(){
            this.url = window.location.host
            const searchValue = document.getElementById('searchSellProduct').value
            if (searchValue.trim().length > 0){
                fetch("/sells/search", {
                    body: JSON.stringify({ searchSells: searchValue }),
                    method: "POST",
                })
                .then((res) => res.json())
                .then((data) => {
                    this.showTable = false
                    this.showPagination = false
                    this.searchedData = true
                    if (data.length === 0) {
                        this.noData = true
                    }else{
                        this.data = data
                    }
                })
            }else{
                this.showTable = true
                this.showPagination = true
                this.searchedData = false
            }
        },

        // suppliers search
        searchSuppliers(){
            this.url = window.location.host
            const searchValue = document.getElementById('searchSupplier').value

            if (searchValue.trim().length > 0){
                fetch("/supplier/search", {
                    body: JSON.stringify({ searchSupplier: searchValue }),
                    method: "POST",
                })
                .then((res) => res.json())
                .then((data) => {
                    this.showTable = false
                    this.showPagination = false
                    this.searchedData = true
                    if (data.length === 0) {
                        this.noData = true
                    }else{
                        this.data = data
                    }
                })
            }else{
                this.showTable = true
                this.showPagination = true
                this.searchedData = false
            }
        }
    },
    delimiters: ['[[', ']]']
}


Vue.createApp(search).mount('#ajax-search')