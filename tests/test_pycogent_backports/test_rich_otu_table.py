#!/usr/bin/env python

from numpy import array, where
from pysparse.spmatrix import ll_mat
from cogent.util.misc import unzip
from cogent.util.unit_test import TestCase, main
from qiime.pycogent_backports.rich_otu_table import TableException, Table, \
    DenseTable, SparseTable, DenseOTUTable, SparseOTUTable, to_ll_mat

__author__ = "Daniel McDonald"
__copyright__ = "Copyright 2007-2011, QIIME"
__credits__ = ["Daniel McDonald", "Jai Rideout", "Justin Kuczynski",
               "Greg Caporaso", "Jose Clemente"]
__license__ = "GPL"
__version__ = "1.3.0dev"
__maintainer__ = "Daniel McDonald"
__email__ = "daniel.mcdonald@colorado.edu"
__status__ = "Prototype"

class SupportTests(TestCase):
    def setUp(self):
        pass

    def test_TableException(self):
        """Make sure a TableException can be raised"""
        def f():
            raise TableException
        self.assertRaises(TableException, f)

    def test_to_ll_mat(self):
        """Convert to expected ll_mat types"""
        input = {(0,1):5,(10,8):-1.23}

        exp = ll_mat(11,9)
        exp[0,1] = 5
        exp[10,8] = -1.23
        obs = to_ll_mat(input)
        self.assertEqual(obs.items(), exp.items())

        # test transpose
        exp = ll_mat(9,11)
        exp[1,0] = 5
        exp[8,10] = -1.23
        obs = to_ll_mat(input, transpose=True)
        self.assertEqual(obs.items(), exp.items())

class TableTests(TestCase):
    def setUp(self):
        self.t1 = Table(array([]),[],[])
        self.t2 = Table(array([]),[],[])
        self.simple_derived = Table(array([[5,6],[7,8]]), [1,2],[3,4])

    def test_verify_metadata(self):
        """Make sure the metadata is sane (including obs/sample ids)"""
        obs_ids = [1,2,3]
        obs_md = [{'a':0},{'b':0},{'c':0}]
        samp_ids = [4,5,6,7]
        samp_md = [{'d':0},{'e':0},{'f':0},{'g':0}]
        d = array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
        t = Table(d, samp_ids, obs_ids, samp_md, obs_md)
        # test is that no exception is raised

        obs_ids = [1,2]
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)

        obs_ids = [1,2,3]
        samp_ids = [4,5,6]
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)
       
        samp_ids = [4,5,6,7]
        obs_md = ['a','b']
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)

        obs_md = ['a','b','c']
        samp_md = ['d','e','f']
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)
        
        obs_md = None
        samp_md = None
        # test is that no exception is raised
        t = Table(d, samp_ids, obs_ids, samp_md, obs_md)

        # do not allow duplicate ids
        obs_ids = [1,1,3]
        samp_ids = [4,5,6]
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)

        obs_ids = [1,2,3]
        samp_ids = [4,4,6]
        self.assertRaises(TableException, Table, d, samp_ids, obs_ids, samp_md,
                          obs_md)
   
    def test_cast_metadata(self):
        """Cast metadata objects to defaultdict to support default values"""
        obs_ids = [1,2,3]
        obs_md = [{'a':1},{'b':2},{'c':3}]
        samp_ids = [4,5,6,7]
        samp_md = [{'d':1},None,{'f':3},{'g':4}]
        d = array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
        t = Table(d, samp_ids, obs_ids, samp_md, obs_md)

        self.assertEqual(t.SampleMetadata[0]['non existent key'], None)
        self.assertEqual(t.SampleMetadata[1]['non existent key'], None)
        self.assertEqual(t.SampleMetadata[2]['non existent key'], None)
        self.assertEqual(t.SampleMetadata[3]['non existent key'], None)
        self.assertEqual(t.ObservationMetadata[0]['non existent key'], None)
        self.assertEqual(t.ObservationMetadata[1]['non existent key'], None)
        self.assertEqual(t.ObservationMetadata[2]['non existent key'], None)

    def test_getitem(self):
        """getitem should work as expeceted"""
        self.assertEqual(self.simple_derived[0,0], 5)
        self.assertEqual(self.simple_derived[1,0], 7)
        self.assertEqual(self.simple_derived[0,1], 6)
        self.assertEqual(self.simple_derived[1,1], 8)
        self.assertRaises(IndexError, self.simple_derived.__getitem__, [1,2])

    def test_setitem(self):
        """setitem should work as expected"""
        self.simple_derived[0,0] *= 2
        self.simple_derived[1,0] *= 2
        self.simple_derived[0,1] *= 2
        self.simple_derived[1,1] *= 2
        
        self.assertRaises(IndexError, self.simple_derived.__setitem__, [1,2], 3)

        self.assertEqual(self.simple_derived[0,0], 10)
        self.assertEqual(self.simple_derived[1,0], 14)
        self.assertEqual(self.simple_derived[0,1], 12)
        self.assertEqual(self.simple_derived[1,1], 16)


    def test_str(self):
        """str is dependent on derived class"""
        self.assertRaises(TableException, str, self.t1)

    def test_iter(self):
        """iter is dependent on derived class"""
        self.assertRaises(NotImplementedError, iter, self.t1)

    def test_iter_obs(self):
        """iter_obs is dependent on derived class"""
        self.assertRaises(NotImplementedError, self.t1._iter_obs)

    def test_iter_samp(self):
        """iter_samp is dependent on derived class"""
        self.assertRaises(NotImplementedError, self.t1._iter_samp)

    def test_conv_to_np(self):
        """conv_to_np is dependent on derived class"""
        self.assertRaises(NotImplementedError, self.t1._conv_to_np, 1)

    def test_iterSamples(self):
        """Iterates samples, not all called methods are implemented in base"""
        gen = self.t1.iterSamples()
        self.assertRaises(NotImplementedError, gen.next)

    def test_iterObservations(self):
        """Iterates obs, not all called methods are implemented in base"""
        gen = self.t1.iterObservations()
        self.assertRaises(NotImplementedError, gen.next)

    def test_filterSamples(self):
        """Filters samples, not all called methods are implemented in base"""
        self.assertRaises(NotImplementedError, self.t1.filterSamples, 1)

    def test_filterObservations(self):
        """Filters obs, not all called methods are implemented in base"""
        self.assertRaises(NotImplementedError, self.t1.filterObservations, 1)

    def test_transformObservations(self):
        """Transform obs, not all called methods are implemented in base"""
        self.assertRaises(NotImplementedError, self.t1.transformObservations,1)
    
    def test_transformSamples(self):
        """Transform samples, not all called methods are implemented in base"""
        self.assertRaises(NotImplementedError, self.t1.transformSamples, 1)
   
    def test_delimitedSelf(self):
        """Test basic string functionality of self"""
        self.assertRaises(TableException, self.t1.delimitedSelf)

    def test_nonzeroBySamples(self):
        """Returns nonzero indices by samples"""
        self.fail()
    def test_nonzeroByObservation(self):
        """Returns nonzero indices by observation"""
        self.fail()
    def test_nonzero(self):
        """Returns nonzero indices within the matrix"""
        self.fail()
    ### ADD TESTS FOR unionBySample, unionByObservation,
    ###               int
class DenseTableTests(TestCase):
    def setUp(self):
        self.dt1 = DenseTable(array([[5,6],[7,8]]), ['a','b'],['1','2'])
        self.dt2 = DenseTable(array([[5,6],[7,8]]), ['a','b'],['1','2'])
        self.dt_rich = DenseTable(array([[5,6],[7,8]]), ['a','b'],['1','2'],
                [{'barcode':'aatt'},{'barcode':'ttgg'}],
                [{'taxonomy':['k__a','p__b']},{'taxonomy':['k__a','p__c']}])
    
    def test_delimitedSelf(self):
        """Print out self in a delimited form"""
        exp = '\n'.join(["#RowIDs\ta\tb","1\t5\t6","2\t7\t8"])
        obs = self.dt1.delimitedSelf()
        self.assertEqual(obs,exp)

    def test_conv_to_np(self):
        """Correctly convert to a numpy type"""
        input = array([1,2,3,4,5])
        exp = array([1,2,3,4,5])
        obs = self.dt1._conv_to_np(input)
        self.assertEqual(obs,exp)

    def test_iter(self):
        """Should iterate over samples"""
        exp = [(array([5,7]), 'a', None), (array([6,8]), 'b', None)]
        obs = list(self.dt1)
        self.assertEqual(obs, exp)

    def test_iter_obs(self):
        """Should iterate over obs"""
        exp = [array([5,6]), array([7,8])]
        obs = list(self.dt1._iter_obs())
        self.assertEqual(obs, exp)

    def test_iter_samp(self):
        """Should iterate over samp"""
        exp = [array([5,7]), array([6,8])]
        obs = list(self.dt1._iter_samp())
        self.assertEqual(obs,exp)

    def test_conv_to_self_type(self):
        """Should convert from other to numpy type"""
        input = [1,2,3]
        exp = array([1,2,3])
        obs = self.dt1._conv_to_self_type(input)
        self.assertEqual(obs, exp)

        # conv_to_self_type doesn't transpose row vectors to col vectors
        # ...need to be in a matrix... ugh
        exp = array([[1],[2],[3]])
        obs = self.dt1._conv_to_self_type([input], transpose=True)
        self.assertEqual(obs, exp)

    def test_eq(self):
        """eq is defined by equality of data matrix, ids and metadata"""
        self.assertTrue(self.dt1 == self.dt2)
        self.dt1.ObservationIds = [1,2,3]
        self.assertFalse(self.dt1 == self.dt2)

        self.dt1.ObservationIds = self.dt2.ObservationIds
        self.dt1._data = array([[1,2],[10,20]])
        self.assertFalse(self.dt1 == self.dt2)

    def test_ne(self):
        """ne is defined by non-equality of data matrix, ids or metadata"""
        self.assertFalse(self.dt1 != self.dt2)
        self.dt1._data = array([[1,2],[10,20]])
        self.assertTrue(self.dt1 != self.dt2)

        self.dt1._data = self.dt2._data
        self.dt1.SampleIds = [10,20,30]
        self.assertTrue(self.dt1 != self.dt2)
    
    def test_iterSamples(self):
        """Iterates samples"""
        gen = self.dt1.iterSamples()
        exp = [(array([5,7]), 'a', None), (array([6,8]), 'b', None)]
        obs = list(gen)
        self.assertEqual(obs, exp)

        gen = self.dt_rich.iterSamples()
        exp = [(array([5,7]), 'a', {'barcode':'aatt'}),
               (array([6,8]), 'b', {'barcode':'ttgg'})]
        obs = list(gen)
        self.assertEqual(obs, exp)

    def test_iterObservations(self):
        """Iterates observations"""
        gen = self.dt1.iterObservations()
        exp = [(array([5,6]), '1', None), (array([7,8]), '2', None)]
        obs = list(gen)
        self.assertEqual(obs, exp)

        gen = self.dt_rich.iterObservations()
        exp = [(array([5,6]), '1', {'taxonomy':['k__a','p__b']}),
               (array([7,8]), '2', {'taxonomy':['k__a','p__c']})]
        obs = list(gen)
        self.assertEqual(obs, exp)

    def test_filterSamples(self):
        """Filters samples by arbitrary function"""
        f_value = lambda v,id_,md: (v <= 5).any()
        f_id = lambda v,id_,md: id_ == 'a'
        f_md = lambda v,id_,md: md['barcode'] == 'ttgg'

        exp_value = DenseTable(array([[5],[7]]), ['a'], ['1','2'], 
                [{'barcode':'aatt'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        exp_id = DenseTable(array([[5],[7]]), ['a'], ['1','2'], 
                [{'barcode':'aatt'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        exp_md = DenseTable(array([[6],[8]]), ['b'], ['1','2'], 
                [{'barcode':'ttgg'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        
        obs_value = self.dt_rich.filterSamples(f_value)
        obs_id = self.dt_rich.filterSamples(f_id)
        obs_md = self.dt_rich.filterSamples(f_md)

        self.assertEqual(obs_value, exp_value)
        self.assertEqual(obs_id, exp_id)
        self.assertEqual(obs_md, exp_md)

        exp_inv = DenseTable(array([[6],[8]]), ['b'], ['1','2'], 
                [{'barcode':'ttgg'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        obs_inv = self.dt_rich.filterSamples(f_value, invert=True)
        self.assertEqual(obs_inv, exp_inv)

    def test_filterObservations(self):
        """Filters observations by arbitrary function"""
        f_value = lambda v,id_,md: (v <= 5).any()
        f_id = lambda v,id_,md: id_ == '1'
        f_md = lambda v,id_,md: md['taxonomy'][1] == 'p__c'

        exp_value = DenseTable(array([[5,6]]), ['a','b'], ['1'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__b']}])
        exp_id = DenseTable(array([[5,6]]), ['a','b'], ['1'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__b']}])
        exp_md = DenseTable(array([[7,8]]), ['a','b'], ['2'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__c']}])
        
        obs_value = self.dt_rich.filterObservations(f_value)
        obs_id = self.dt_rich.filterObservations(f_id)
        obs_md = self.dt_rich.filterObservations(f_md)

        self.assertEqual(obs_value, exp_value)
        self.assertEqual(obs_id, exp_id)
        self.assertEqual(obs_md, exp_md)

        exp_inv = DenseTable(array([[7,8]]), ['a','b'], ['2'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__c']}])
        obs_inv = self.dt_rich.filterObservations(f_value, invert=True)
        self.assertEqual(obs_inv, exp_inv)

    def test_transformObservations(self):
        """Transform observations by arbitrary function"""
        transform_f = lambda x: where(x >= 7, 1, 0)
        exp = DenseTable(array([[0,0],[1,1]]), ['a','b'], ['1','2'])
        obs = self.dt1.transformObservations(transform_f)

        self.assertEqual(obs, exp)
    
    def test_transformSamples(self):
        """Transform samples by arbitrary function"""
        transform_f = lambda x: where(x >= 6, 1, 0)
        exp = DenseTable(array([[0,1],[1,1]]), ['a','b'], ['1','2'])
        obs = self.dt1.transformSamples(transform_f)
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject(self):
        """Should throw an exception because there is no table type."""
        self.assertRaises(TableException, self.dt1.getBiomFormatObject)
        self.assertRaises(TableException, self.dt_rich.getBiomFormatObject)

    def test_binSamplesByMetadata(self):
        """Yield tables binned by sample metadata"""
        f = lambda x: x['age']
        obs_ids = ['a','b','c','d']
        samp_ids = ['1','2','3','4']
        data = array([[1,2,3,4],[5,6,7,8],[8,9,10,11],[12,13,14,15]])
        obs_md = [{},{},{},{}]
        samp_md = [{'age':2},{'age':4},{'age':2},{}]
        t = DenseTable(data, samp_ids, obs_ids, samp_md, obs_md)
        obs_bins, obs_tables = unzip(t.binSamplesByMetadata(f))

        exp_bins = ((2), (4), (None))
        exp1_data = array([[1,3],[5,7],[8,10],[12,14]])
        exp1_obs_ids = ['a','c']
        exp1_samp_ids = ['1','2','3','4']
        exp1_obs_md = [{},{},{},{}]

        exp1 = DenseTable(exp_data)
        
    def test_binObservationsByMetadata(self):
        """Yield tables binned by observation metadata"""
        def make_level_f(level):
            def f(metadata):
                return metadata['taxonomy'][:level]
            return f

        func_king = make_level_f(1)
        func_phy = make_level_f(2)

        obs_ids = ['a','b','c']
        samp_ids = [1,2,3]
        data = array([[1,2,3],[4,5,6],[7,8,9]])
        obs_md = [{"taxonomy":['k__a','p__b','c__c']},
                  {"taxonomy":['k__a','p__b','c__d']},
                  {"taxonomy":['k__a','p__c','c__e']}]
        t = DenseTable(data, samp_ids, obs_ids, ObservationMetadata=obs_md)

        exp_king_obs_ids = ['a','b','c']
        exp_king_samp_ids = [1,2,3]
        exp_king_data = array([[1,2,3],[4,5,6],[7,8,9]])
        exp_king_obs_md = [{"taxonomy":['k__a','p__b','c__c']},
                           {"taxonomy":['k__a','p__b','c__d']},
                           {"taxonomy":['k__a','p__c','c__e']}]
        exp_king = DenseTable(data, exp_king_samp_ids, exp_king_obs_ids, 
                              ObservationMetadata=exp_king_obs_md)
        obs_bins, obs_king = unzip(t.binObservationsByMetadata(func_king))
        self.assertEqual(obs_king, [exp_king])
        self.assertEqual(obs_bins, [tuple(['k__a'])])

        exp_phy1_obs_ids = ['a','b']
        exp_phy1_samp_ids = [1,2,3]
        exp_phy1_data = array([[1,2,3],[4,5,6]])
        exp_phy1_obs_md = [{"taxonomy":['k__a','p__b','c__c']},
                           {"taxonomy":['k__a','p__b','c__d']}]
        exp_phy1 = DenseTable(exp_phy1_data, exp_phy1_samp_ids, 
                              exp_phy1_obs_ids, 
                              ObservationMetadata=exp_phy1_obs_md)
        exp_phy2_obs_ids = ['c']
        exp_phy2_samp_ids = [1,2,3]
        exp_phy2_data = array([[7,8,9]])
        exp_phy2_obs_md = [{"taxonomy":['k__a','p__c','c__e']}]
        exp_phy2 = DenseTable(exp_phy2_data, exp_phy2_samp_ids,exp_phy2_obs_ids,
                               ObservationMetadata=exp_phy2_obs_md)
        obs_bins, obs_phy = unzip(t.binObservationsByMetadata(func_phy))
        self.assertEqual(obs_phy, [exp_phy1, exp_phy2])
        self.assertEqual(obs_bins, [('k__a','p__b'),('k__a','p__c')])

class SparseTableTests(TestCase):
    def setUp(self):
        self.vals = {(0,0):5,(0,1):6,(1,0):7,(1,1):8}
        self.st1 = SparseTable(to_ll_mat(self.vals),
                               ['a','b'],['1','2'])
        self._to_dict_f = lambda x: x.items()
        self.st_rich = SparseTable(to_ll_mat(self.vals), 
                ['a','b'],['1','2'],
                [{'barcode':'aatt'},{'barcode':'ttgg'}],
                [{'taxonomy':['k__a','p__b']},{'taxonomy':['k__a','p__c']}])

    def test_delimitedSelf(self):
        """Print out self in a delimited form"""
        exp = '\n'.join(["#RowIDs\ta\tb","1\t5.0\t6.0","2\t7.0\t8.0"])
        obs = self.st1.delimitedSelf()
        self.assertEqual(obs,exp)

    def test_conv_to_np(self):
        """Should convert a self styled vector to numpy type"""
        input_row = ll_mat(1,3)
        input_row[0,0] = 10
        exp = array([10.0, 0, 0])
        obs = self.st1._conv_to_np(input_row)
        self.assertEqual(obs, exp)

        input_col = ll_mat(3,1)
        input_col[0,0] = 12
        exp = array([12.0, 0, 0])
        obs = self.st1._conv_to_np(input_col)
        self.assertEqual(obs, exp)

    def test_conv_to_self_type(self):
        """Should convert other to ll_mat type"""
        exp = ll_mat(2,2)
        exp[0,0] = 5
        exp[0,1] = 6
        exp[1,0] = 7
        exp[1,1] = 8        
        obs = self.st1._conv_to_self_type(self.vals)
        self.assertEqual(obs.items(), exp.items())

        exp = ll_mat(2,2)
        exp[0,0] = 5
        exp[0,1] = 7
        exp[1,0] = 6
        exp[1,1] = 8        
        obs = self.st1._conv_to_self_type(self.vals, transpose=True)
        self.assertEqual(obs.items(), exp.items())

        exp = ll_mat(2,2)
        exp[0,0] = 5
        exp[0,1] = 6
        exp[1,0] = 7
        exp[1,1] = 8
        obs = self.st1._conv_to_self_type([((0,0),5),((0,1),6),
                                           ((1,0),7),((1,1),8)])
        self.assertEqual(obs.items(), exp.items())

        # passing a single vector
        exp = ll_mat(1,3)
        exp[0,0] = 2
        exp[0,1] = 0
        exp[0,2] = 3
        obs = self.st1._conv_to_self_type(array([2,0,3]))
        self.assertEqual(obs.items(), exp.items())

        # passing a list of dicts
        exp = ll_mat(2,3)
        exp[0,0] = 5
        exp[0,1] = 6
        exp[0,2] = 7
        exp[1,0] = 8
        exp[1,1] = 9
        exp[1,2] = 10
        obs = self.st1._conv_to_self_type([{(0,0):5,(0,1):6,(0,2):7},
                                           {(1,0):8,(1,1):9,(1,2):10}])
        self.assertEqual(obs.items(), exp.items()) 

        # passing a list of dicts, transpose
        exp = ll_mat(3,2)
        exp[0,0] = 5
        exp[1,0] = 6
        exp[2,0] = 7
        exp[0,1] = 8
        exp[1,1] = 9
        exp[2,1] = 10
        obs = self.st1._conv_to_self_type([{(0,0):5,(0,1):6,(0,2):7},
                                           {(1,0):8,(1,1):9,(1,2):10}],
                                           transpose=True)
        self.assertEqual(obs.items(), exp.items())

        # passing a list of ll_mat vectors. UGH
        exp = ll_mat(2,3)
        exp[0,0] = 5
        exp[0,1] = 6
        exp[0,2] = 7
        exp[1,0] = 8
        exp[1,1] = 9
        exp[1,2] = 10
        row1 = ll_mat(1,3)
        row1[0,0] = 5
        row1[0,1] = 6
        row1[0,2] = 7
        row2 = ll_mat(1,3)
        row2[0,0] = 8
        row2[0,1] = 9
        row2[0,2] = 10
        obs = self.st1._conv_to_self_type([row1, row2])
        self.assertEqual(obs.items(), exp.items()) 
        
        self.fail("much of these tests should be pushed to test_to_ll_mat")

    def test_iter(self):
        """Should iterate over samples"""
        exp = [(array([5,7]), 'a', None), (array([6,8]), 'b', None)]
        obs = list(self.st1)
        self.assertEqual(obs, exp)

    def test_iter_obs(self):
        """Iterate over observations of sparse matrix"""
        r1 = ll_mat(1,2)
        r2 = ll_mat(1,2)
        r1[0,0] = 5
        r1[0,1] = 6
        r2[0,0] = 7
        r2[0,1] = 8

        exp = map(self._to_dict_f, [r1, r2])
        obs = map(self._to_dict_f, self.st1._iter_obs())

        self.assertEqual(obs, exp)

    def test_iter_samp(self):
        """Iterate over samples of sparse matrix"""
        c1 = ll_mat(1,2)
        c2 = ll_mat(1,2)
        c1[0,0] = 5
        c1[0,1] = 7
        c2[0,0] = 6
        c2[0,1] = 8
        exp = map(self._to_dict_f, [c1, c2])
        obs = map(self._to_dict_f, self.st1._iter_samp())

        self.assertEqual(obs, exp)

    def test_iterSamples(self):
        """Iterates samples"""
        gen = self.st1.iterSamples()
        exp = [(array([5,7]), 'a', None), (array([6,8]), 'b', None)]
        obs = list(gen)
        self.assertEqual(obs, exp)

        gen = self.st_rich.iterSamples()
        exp = [(array([5,7]), 'a', {'barcode':'aatt'}),
               (array([6,8]), 'b', {'barcode':'ttgg'})]
        obs = list(gen)
        self.assertEqual(obs, exp)

        # [[1,2,3],[1,0,2]] isn't yielding column 2 correctly
        self.st1[1,0] = 0
        gen = self.st1.iterSamples()
        exp = [(array([5,0]), 'a', None), (array([6,8]), 'b', None)]
        obs = list(gen)
        self.assertEqual(obs, exp)

    def test_iterObservations(self):
        """Iterates observations"""
        gen = self.st1.iterObservations()
        exp = [(array([5,6]), '1', None), (array([7,8]), '2', None)]
        obs = list(gen)
        self.assertEqual(obs, exp)

        gen = self.st_rich.iterObservations()
        exp = [(array([5,6]), '1', {'taxonomy':['k__a','p__b']}),
               (array([7,8]), '2', {'taxonomy':['k__a','p__c']})]
        obs = list(gen)
        self.assertEqual(obs, exp)

    def test_filterSamples(self):
        """Filters samples by arbitrary function"""
        f_value = lambda v,id_,md: (v <= 5).any()
        f_id = lambda v,id_,md: id_ == 'a'
        f_md = lambda v,id_,md: md['barcode'] == 'ttgg'

        val_ll_mat = to_ll_mat({(0,0):5,(1,0):7})
        exp_value = SparseTable(val_ll_mat, ['a'], ['1','2'], 
                [{'barcode':'aatt'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        id_ll_mat = to_ll_mat({(0,0):5,(1,0):7})
        exp_id = SparseTable(id_ll_mat, ['a'], ['1','2'], 
                [{'barcode':'aatt'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        md_ll_mat = to_ll_mat({(0,0):6,(1,0):8})
        exp_md = SparseTable(md_ll_mat, ['b'], ['1','2'], 
                [{'barcode':'ttgg'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        
        obs_value = self.st_rich.filterSamples(f_value)
        obs_id = self.st_rich.filterSamples(f_id)
        obs_md = self.st_rich.filterSamples(f_md)

        self.assertEqual(obs_value, exp_value)
        self.assertEqual(obs_id, exp_id)
        self.assertEqual(obs_md, exp_md)

        inv_ll_mat = to_ll_mat({(0,0):6,(1,0):8})
        exp_inv = SparseTable(inv_ll_mat, ['b'], ['1','2'], 
                [{'barcode':'ttgg'}], [{'taxonomy':['k__a','p__b']},
                                       {'taxonomy':['k__a','p__c']}])
        obs_inv = self.st_rich.filterSamples(f_value, invert=True)
        self.assertEqual(obs_inv, exp_inv)
        
    def test_filterObservations(self):
        """Filters observations by arbitrary function"""
        f_value = lambda v,id_,md: (v <= 5).any()
        f_id = lambda v,id_,md: id_ == '1'
        f_md = lambda v,id_,md: md['taxonomy'][1] == 'p__c'

        val_ll_mat = to_ll_mat({(0,0):5,(0,1):6})
        exp_value = SparseTable(val_ll_mat, ['a','b'], ['1'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__b']}])
        id_ll_mat = to_ll_mat({(0,0):5,(0,1):6})
        exp_id = SparseTable(id_ll_mat, ['a','b'], ['1'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__b']}])
        md_ll_mat = to_ll_mat({(0,0):7,(0,1):8})
        exp_md = SparseTable(md_ll_mat, ['a','b'], ['2'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__c']}])
        
        obs_value = self.st_rich.filterObservations(f_value)
        obs_id = self.st_rich.filterObservations(f_id)
        obs_md = self.st_rich.filterObservations(f_md)

        self.assertEqual(obs_value, exp_value)
        self.assertEqual(obs_id, exp_id)
        self.assertEqual(obs_md, exp_md)

        inv_ll_mat = to_ll_mat({(0,0):7,(0,1):8})
        exp_inv = SparseTable(inv_ll_mat, ['a','b'], ['2'], 
                [{'barcode':'aatt'},{'barcode':'ttgg'}], 
                [{'taxonomy':['k__a','p__c']}])
        obs_inv = self.st_rich.filterObservations(f_value, invert=True)
        self.assertEqual(obs_inv, exp_inv)

    def test_transformObservations(self):
        """Transform observations by arbitrary function"""
        transform_f = lambda x: where(x >= 7, 1, 0)
        sp_ll_mat = to_ll_mat({(0,0):0,(0,1):0,(1,0):1,(1,1):1})
        exp = SparseTable(sp_ll_mat, ['a','b'], ['1','2'])
        obs = self.st1.transformObservations(transform_f)
        self.assertEqual(obs, exp)
    
    def test_transformSamples(self):
        """Transform samples by arbitrary function"""
        transform_f = lambda x: where(x >= 6, 1, 0)
        sp_ll_mat = to_ll_mat({(0,0):0,(0,1):1,(1,0):1,(1,1):1})
        exp = SparseTable(sp_ll_mat, ['a','b'], ['1','2'])
        obs = self.st1.transformSamples(transform_f)
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject(self):
        """Should throw an exception because there is no table type."""
        self.assertRaises(TableException, self.st1.getBiomFormatObject)
        self.assertRaises(TableException, self.st_rich.getBiomFormatObject)
    
    def test_binSamplesByMetadata(self):
        self.fail("tested in DenseTable, needed in Sparse tests?")
    def test_binObservationsByMetadata(self):
        self.fail("tested in DenseTable, needed in Sparse tests?")

class DenseOTUTableTests(TestCase):
    def setUp(self):
        self.dot_min = DenseOTUTable(array([[5,6],[7,8]]), ['a','b'],['1','2'])
        self.dot_rich = DenseOTUTable(array([[5,6],[7,8]]),
                ['a','b'],['1','2'], [{'barcode':'aatt'},{'barcode':'ttgg'}],
                [{'taxonomy':['k__a','p__b']},{'taxonomy':['k__a','p__c']}])
        self.empty_table = DenseOTUTable(array([]), [], [])
        self.partial_table1 = DenseOTUTable(array([[0,2],[9,10]]),
                ['a','b'],['1','2'],
                SampleMetadata=[{'barcode':'aatt'},{'barcode':'ttgg'}],
                TableId="TestTable1")
        self.partial_table2 = DenseOTUTable(array([[0,2],[9,10]]),
                ['a','b'],['1','2'], ObservationMetadata=[{'taxonomy':
                    ['k__a','p__b']},{'taxonomy':['k__a','p__c']}],
                TableId="TestTable2")
        self.float_table = DenseOTUTable(
                array([[0.0,2.5,3.4],[9.3,10.23,2.2]]),['a','b','c'],['1','2'])
        self.str_table = DenseOTUTable(
                array([['val1','val2'],['val3','val4']]),['Samp1','Samp2'],
                ['Obs1','Obs2'])
        self.invalid_element_type_table = DenseOTUTable(
                array([[{}],[{}]]),['a'],['1','2'])

    def test_getBiomFormatObject_minimal(self):
        """Should return a dictionary of the minimal table in Biom format."""
        exp = {'rows': [{'id': '1', 'metadata': None},
            {'id': '2', 'metadata': None}],
            'format': 'Biological Observation Matrix v0.9',
            'data': [[5, 6], [7, 8]],
            'columns': [{'id': 'a', 'metadata': None},
                {'id': 'b', 'metadata': None}],
            'matrix_type': 'dense', 'shape': [2, 2],
            'format_url': 'http://www.qiime.org/svn_documentation/' +\
                    'documentation/biom_format.html',
            'type': 'OTU table', 'id': None, 'matrix_element_type': 'int'}
        obs = self.dot_min.getBiomFormatObject()
        # Remove keys that we don't want to test because they might change
        # frequently (and the date is impossible to test). By using 'del', this
        # also tests that the key exists.
        del obs['date']
        del obs['generated_by']
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject_rich(self):
        """Should return a dictionary of the rich table in Biom format."""
        exp = {'rows': [{'id': '1',
            'metadata': {'taxonomy': ['k__a', 'p__b']}},
            {'id': '2', 'metadata': {'taxonomy': ['k__a', 'p__c']}}],
            'format': 'Biological Observation Matrix v0.9',
            'data': [[5, 6], [7, 8]], 'columns': [{'id': 'a', 'metadata':
                {'barcode': 'aatt'}}, {'id': 'b', 'metadata':
                    {'barcode': 'ttgg'}}],
                'matrix_type': 'dense', 'shape': [2, 2],
                'format_url': 'http://www.qiime.org/svn_documentation/' +\
                        'documentation/biom_format.html',
                'type': 'OTU table', 'id': None, 'matrix_element_type': 'int'}
        obs = self.dot_rich.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject_empty_data(self):
        """Should return a dictionary of the empty table in Biom format."""
        exp = {'rows': [], 'format': 'Biological Observation Matrix v0.9',
                'data': [], 'columns': [],
                'matrix_type': 'dense', 'shape': [0, 0],
                'format_url': 'http://www.qiime.org/svn_documentation/' +\
                        'documentation/biom_format.html', 'type': 'OTU table',
                        'id': None, 'matrix_element_type': 'int'}
        obs = self.empty_table.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject_partial_metadata(self):
        """Should return a dictionary of the partial metadata table."""
        exp1 = {'rows': [{'id': '1', 'metadata': None},
            {'id': '2', 'metadata': None}], 'format':
            'Biological Observation Matrix v0.9', 'data': [[0, 2], [9, 10]],
            'columns': [{'id': 'a', 'metadata': {'barcode': 'aatt'}},
                {'id': 'b', 'metadata': {'barcode': 'ttgg'}}], 'matrix_type':
            'dense', 'shape': [2, 2], 'format_url':
            'http://www.qiime.org/svn_documentation/documentation/' +\
                    'biom_format.html', 'type': 'OTU table', 'id':
                    'TestTable1', 'matrix_element_type': 'int'}
        obs1 = self.partial_table1.getBiomFormatObject()
        del obs1['date']
        del obs1['generated_by']
        self.assertEqual(obs1, exp1)

        exp2 = {'rows': [{'id': '1', 'metadata':
            {'taxonomy': ['k__a', 'p__b']}}, {'id': '2', 'metadata':
                {'taxonomy': ['k__a', 'p__c']}}], 'format':
            'Biological Observation Matrix v0.9', 'data': [[0, 2], [9, 10]],
            'columns': [{'id': 'a', 'metadata': None},
                {'id': 'b', 'metadata': None}], 'matrix_type': 'dense',
            'shape': [2, 2], 'format_url':
            'http://www.qiime.org/svn_documentation/documentation/' +\
                    'biom_format.html', 'type': 'OTU table',
                    'id': 'TestTable2', 'matrix_element_type': 'int'}
        obs2 = self.partial_table2.getBiomFormatObject()
        del obs2['date']
        del obs2['generated_by']
        self.assertEqual(obs2, exp2)

    def test_getBiomFormatObject_float(self):
        """Should return a dictionary of the table with float values."""
        exp = {'rows': [{'id': '1', 'metadata': None},
            {'id': '2', 'metadata': None}], 'format':
            'Biological Observation Matrix v0.9', 'data':
            [[0.0, 2.5, 3.3999999999999999], [9.3000000000000007, 10.23,
                2.2000000000000002]], 'columns':
            [{'id': 'a', 'metadata': None}, {'id': 'b', 'metadata': None},
                {'id': 'c', 'metadata': None}], 'matrix_type': 'dense',
            'shape': [2, 3], 'format_url':
            'http://www.qiime.org/svn_documentation/documentation/' +\
                    'biom_format.html', 'type': 'OTU table', 'id': None,
                    'matrix_element_type': 'float'}
        obs = self.float_table.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertFloatEqual(obs, exp)

    def test_getBiomFormatObject_str(self):
        """Should return a dictionary of the table with string values."""
        exp = {'rows': [{'id': 'Obs1', 'metadata': None},
            {'id': 'Obs2', 'metadata': None}],
            'format': 'Biological Observation Matrix v0.9', 'data':
            [['val1', 'val2'], ['val3', 'val4']], 'columns':
            [{'id': 'Samp1', 'metadata': None},
                {'id': 'Samp2', 'metadata': None}], 'matrix_type':
            'dense', 'shape': [2, 2], 'format_url':
            'http://www.qiime.org/svn_documentation/documentation/' +\
                    'biom_format.html', 'type': 'OTU table', 'id': None,
                    'matrix_element_type': 'str'}
        obs = self.str_table.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertEqual(obs, exp)

    def test_getBiomFormatObject_invalid_element_type(self):
        """Should throw an exception if the element type isn't valid."""
        self.assertRaises(TableException,
                self.invalid_element_type_table.getBiomFormatObject)

class SparseOTUTableTests(TestCase):
    def setUp(self):
        self.vals = {(0,0):5,(1,0):7,(1,1):8}
        self.sot_min = SparseOTUTable(to_ll_mat(self.vals), ['a','b'],['1','2'])
        self.sot_rich = SparseOTUTable(to_ll_mat(self.vals), 
                ['a','b'],['1','2'],
                [{'barcode':'aatt'},{'barcode':'ttgg'}],
                [{'taxonomy':['k__a','p__b']},{'taxonomy':['k__a','p__c']}])
        self.float_table = SparseOTUTable(to_ll_mat({(0,1):2.5,(0,2):3.4,(1,0):9.3,
            (1,1):10.23,(1,2):2.2}),['a','b','c'],['1','2'])

    def test_getBiomFormatObject_minimal(self):
        """Should return a dictionary of the minimal table in Biom format."""
        exp = {'rows': [{'id': '1', 'metadata': None},
            {'id': '2', 'metadata': None}],
            'format': 'Biological Observation Matrix v0.9',
            'data': [[0, 0, 5.0], [1, 0, 7.0], [1, 1, 8.0]],
            'columns': [{'id': 'a', 'metadata': None},
                {'id': 'b', 'metadata': None}],
            'matrix_type': 'sparse', 'shape': [2, 2],
            'format_url': 'http://www.qiime.org/svn_documentation/' +\
                    'documentation/biom_format.html',
            'type': 'OTU table', 'id': None, 'matrix_element_type': 'float'}
        obs = self.sot_min.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertFloatEqual(obs, exp)

    def test_getBiomFormatObject_rich(self):
        """Should return a dictionary of the rich table in Biom format."""
        exp = {'rows': [{'id': '1',
            'metadata': {'taxonomy': ['k__a', 'p__b']}},
            {'id': '2', 'metadata': {'taxonomy': ['k__a', 'p__c']}}],
            'format': 'Biological Observation Matrix v0.9',
            'data': [[0, 0, 5.0], [1, 0, 7.0], [1, 1, 8.0]],
            'columns': [{'id': 'a', 'metadata':
                {'barcode': 'aatt'}}, {'id': 'b', 'metadata':
                    {'barcode': 'ttgg'}}],
                'matrix_type': 'sparse', 'shape': [2, 2],
                'format_url': 'http://www.qiime.org/svn_documentation/' +\
                        'documentation/biom_format.html',
                'type': 'OTU table', 'id': None,
                'matrix_element_type': 'float'}
        obs = self.sot_rich.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertFloatEqual(obs, exp)

    def test_getBiomFormatObject_float(self):
        """Should return a dictionary of the table with float values."""
        exp = {'rows': [{'id': '1', 'metadata': None},
            {'id': '2', 'metadata': None}], 'format':
            'Biological Observation Matrix v0.9', 'data':
            [[0, 1, 2.5], [0, 2, 3.3999999999999999],
                [1, 0, 9.3000000000000007], [1, 1, 10.23],
                [1, 2, 2.2000000000000002]], 'columns':
            [{'id': 'a', 'metadata': None}, {'id': 'b', 'metadata': None},
                {'id': 'c', 'metadata': None}], 'matrix_type': 'sparse',
            'shape': [2, 3], 'format_url':
            'http://www.qiime.org/svn_documentation/documentation/' +\
                    'biom_format.html', 'type': 'OTU table', 'id': None,
                    'matrix_element_type': 'float'}
        obs = self.float_table.getBiomFormatObject()
        del obs['date']
        del obs['generated_by']
        self.assertFloatEqual(obs, exp)

if __name__ == '__main__':
    main()