import { connect } from 'dva';
import React, { Component } from 'react';
import { Dispatch } from 'redux';
import SearchHeader from './componets/Search';
import SearchBody from './componets/Result';

interface VisualizationState {}

interface VisualizationProps {
  loading: boolean;
  visualization: VisualizationResult;
  dispatch: Dispatch<any>;
}

@connect(
  ({
    visualization,
    loading,
  }: {
    visualization: VisualizationResult;
    loading: { effects: { [key: string]: boolean } };
  }) => ({ visualization, loading: loading.effects['visualization/fetchTables'] }),
)
class Visualization extends Component<VisualizationProps, VisualizationState> {
  public state: VisualizationState = {};

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch({
      type: 'visualization/fetchTables',
    });
  }

  render() {
    // @ts-ignore
    return (
      <div>
        <SearchHeader />
        <SearchBody />
      </div>
    );
  }
}

export default Visualization;
