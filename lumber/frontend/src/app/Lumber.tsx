import * as React from 'react';
import { Badge, Col, Container, OverlayTrigger, Popover, Row } from 'react-bootstrap';
import { FaTree } from "@react-icons/all-files/fa/FaTree";
import { FaFilter } from "@react-icons/all-files/fa/FaFilter";
import Select from 'react-select'
import { OptionProps } from 'react-select/src/types';

const moment = require('moment')
const queryString = require('query-string');

class App {
    id: string
    name: string
}

class Record {
    id: string
    funcname: string
    level: number
    lineno: number
    message: string
    name: string
    pathname: string
    process: number
    processname: string
    thread: number
    threadname: string
    created: Date
}

type Props = {}

type State = {
    apps: Array<App>,
    records: Array<Record>,
    app: string,
    offset: number,
    size: number,
    total: number,
    showFilters: boolean,
    filters: Array<Filter>,
}

export default class Lumber extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props)
        this.state = {
            apps: [],
            records: [],
            offset: 0,
            size: 0,
            total: 0,
            app: '',
            showFilters: false,
            filters: [],
        }
    }

    componentDidUpdate(prevPros: Props, prevState: State) {
        const app = this.state.apps.filter((rhs) => this.state.app == rhs.id)[0]
        if (prevState.app != this.state.app) {
            this.setState({
                records: [],
                total: 0,
                size: 0,
            })
            this.fetchLogs(app, 0)
        } else if (prevState.filters != this.state.filters) {
            this.setState({
                records: [],
                total: 0,
                size: 0,
            })

            this.fetchLogs(app, 0)
        }
    }

    fetchLogs(app: App, offset: number) {
        const filters = this.state.filters.map((filter) => {
            return filter.column + ',' + filter.operand + ',' + filter.value
        })
        const search = queryString.stringify({
            'offset': offset,
            'filters': filters, //['level,in,10'],
        })
        const url = '/lumber/api/logs/' + app.id + '?' + search
        fetch(url)
            .then(response => {
                if (response.status >= 400) {
                    throw new Error("Failed to retrieve logs")
                }
                return response.json()
            })
            .then(response => {
                console.log(response)
                this.setState((state) => {
                    const records = state.records
                    records.push(...response.records)
                    return {
                        offset: offset,
                        records: records,
                        total: response.total,
                        size: response.size,
                    }
                })
            }, err => {
                // TODO
            })
    }

    fetchApps() {
        const url = '/lumber/api/apps'
        fetch(url)
            .then(response => {
                if (response.status >= 400) {
                    throw new Error("Failed to retrieve apps")
                }
                return response.json()
            })
            .then(response => {
                console.log(response)
                this.setState((state) => {
                    let app = ''
                    if (response.apps.length > 0) {
                        app = response.apps[0].id
                    }
                    return {
                        app: app,
                        apps: response.apps,
                    }
                })
            }, err => {
                // TODO
            })

    }

    handleApp(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({
            app: event.target.value,
        })
    }

    handleLoadMore(event: React.MouseEvent<HTMLAnchorElement>) {
        event.preventDefault()

        const app = this.state.apps.filter((rhs) => this.state.app == rhs.id)[0]
        this.fetchLogs(app, this.state.offset + this.state.size)

    }

    onFiltersUpdated(filters: Array<Filter>) {
        this.setState({
            filters: filters,
        })
    }

    handleToggleFilter(event: React.MouseEvent<HTMLAnchorElement>) {
        event.preventDefault()
        this.setState((state) => {
            return {
                showFilters: !state.showFilters,
            }
        })
    }

    componentDidMount() {
        this.fetchApps()
    }

    render() {
        return (
            <Container fluid>
                <Row>
                    <Col><h1 className="font-weight-bolder"><FaTree /> Lumber</h1></Col>

                    <Col className="text-right pt-2" sm={2}>
                        <Row>
                            <Col>
                                <select className="custom-select" value={this.state.app} onChange={this.handleApp.bind(this)}>
                                    {this.state.apps.map((app) => {
                                        return (
                                            <option key={app.id} value={app.id}>{app.name}</option>
                                        )
                                    })}
                                </select>
                            </Col>
                            <Col sm={1} className="mr-2 pt-1">
                                <a href="#" onClick={this.handleToggleFilter.bind(this)}><FaFilter /></a>
                            </Col>
                        </Row>
                    </Col>
                </Row>
                { this.state.showFilters &&
                    <Row className="mb-2">
                        <Col><FilterBar filters={this.state.filters} onFiltersUpdated={this.onFiltersUpdated.bind(this)} /></Col>
                    </Row>
                }
                <Row>
                    <Col>
                        {this.state.records.map((record, index) => {
                            return (
                                <RecordRow key={index} record={record} />
                            )
                        })}
                        {this.state.offset < this.state.total - this.state.size &&
                            <Row>
                                <Col sm={6} style={{ flex: 'inherit', width: 380 }}></Col>
                                <Col className="text-left"><a href="" onClick={this.handleLoadMore.bind(this)}>Load More</a></Col>
                            </Row>
                        }
                    </Col>
                </Row>
            </Container>
        )
    }
}

type RecordRowProps = {
    record: Record
}

class RecordRow extends React.Component<RecordRowProps> {
    render() {
        const popover = (
            <Popover id={`info-${this.props.record.id}`} style={{ width: 800, maxWidth: 800 }}>
                <Popover.Content>
                    <table className="table">
                        <tbody>
                            <tr>
                                <td>File</td>
                                <td>{this.props.record.pathname}</td>
                            </tr>
                            <tr>
                                <td>Function</td>
                                <td>{this.props.record.funcname}</td>
                            </tr>
                            <tr>
                                <td>Line</td>
                                <td>{this.props.record.lineno}</td>
                            </tr>
                            <tr>
                                <td>Process</td>
                                <td>{this.props.record.processname} ({this.props.record.process})</td>
                            </tr>
                            <tr>
                                <td>Thread</td>
                                <td>{this.props.record.threadname} ({this.props.record.thread})</td>
                            </tr>
                        </tbody>
                    </table>
                </Popover.Content>
            </Popover>
        )

        return (
            <Row className="border-bottom text-monospace">
                <Col sm={3} style={{ flex: 'inherit', width: 210 }}>
                    <small>{moment(this.props.record.created).format('YYYY/MM/DD HH:mm:ss:SSS')}</small>
                </Col>
                <Col sm={1} style={{ flex: 'inherit', width: 30 }}>
                    <LogLevel level={this.props.record.level} />
                </Col>
                <Col sm={2} style={{ flex: 'inherit', width: 140 }} className="text-truncate">
                    <OverlayTrigger trigger={["click", 'focus']} placement="bottom" overlay={popover}>
                        <small>{this.props.record.name}</small>
                    </OverlayTrigger>
                </Col>
                <Col>{this.props.record.message}</Col>
            </Row>
        )
    }
}

type LogLevelProps = {
    level: number
}

class LogLevel extends React.Component<LogLevelProps> {
    render() {
        switch (this.props.level) {
            case 10:
                return <Badge pill variant="secondary">D</Badge>
            case 20:
                return <Badge pill variant="info">I</Badge>
            case 30:
                return <Badge pill variant="warning">W</Badge>
            case 40:
                return <Badge pill variant="danger">E</Badge>
            case 50:
                return <Badge pill variant="danger">C</Badge>
        }
    }
}

enum Column {
    None = '',
    Level = 'level',
}

enum Operand {
    None = '',
    In = 'in',
}

class Filter {
    column: Column
    operand: Operand
    value: Object

    constructor(column: Column, operand: Operand, value: Object) {
        this.column = column
        this.operand = operand
        this.value = value
    }
}

type FilterBarProps = {
    filters: Array<Filter>,
    onFiltersUpdated: (filters: Array<Filter>) => void,
}

type LevelOption = {
    value: number,
    label: string,
}

function levelName(level: number) {
    switch (level) {
        case 10: return 'Debug'
        case 20: return 'Info'
        case 30: return 'Warning'
        case 40: return 'Error'
        case 50: return 'Critical'
    }
}

class FilterBar extends React.Component<FilterBarProps> {
    handleLevelChange(selected: Array<OptionProps>) {
        const filters = this.props.filters.filter((filter) => filter.column != Column.Level)
        if (selected.length > 0) {
            filters.push(
                new Filter(Column.Level, Operand.In, selected.map((option) => option.value).join(',')),
            )
        }
        this.props.onFiltersUpdated(filters)
    }

    render() {
        console.log('Filter', this.props.filters)
        let levelValue: Array<LevelOption> = []
        // Convert the provided filters, into values for the different columns
        for (let filter of this.props.filters) {
            if (filter.column == Column.Level) {
                // Set the levelValue
                levelValue = (filter.value as string).split(',').map((level) => { return { value: parseInt(level), label: levelName(parseInt(level)) } })
            }
        }

        // const levelValue = this.state.levels.map((level) => { return {value: level.value, label: level.label}} )
        const levelOptions: Array<LevelOption> = [
            { value: 10, label: levelName(10) },
            { value: 20, label: levelName(20) },
            { value: 30, label: levelName(30) },
            { value: 40, label: levelName(40) },
            { value: 50, label: levelName(50) },
        ]
        return (
            <Row>
                <Col sm={3}>
                    { /* Level */}
                    <Select options={levelOptions} isMulti value={levelValue} onChange={this.handleLevelChange.bind(this)} />
                    <small className="text-muted">Level</small>
                </Col>
            </Row>
        )
    }
}